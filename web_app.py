import tempfile
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from classifiers import classify_image_openai, classify_image_simulated, create_openai_client
from config import (
    CLASSIFICATION_PROMPT,
    IMAGE_DETAIL,
    MODEL,
    USE_SIMULATED_PREDICTIONS,
    require_openai_api_key,
)
from image_metadata import extract_image_attributes


SUPPORTED_UPLOAD_TYPES = ["jpg", "jpeg", "png", "webp"]
VISIBLE_COLUMNS = [
    "file_name",
    "format",
    "size_kb",
    "width",
    "height",
    "latitude",
    "longitude",
    "classification",
    "alert_status",
]


@st.cache_resource
def get_client():
    if USE_SIMULATED_PREDICTIONS:
        return None
    return create_openai_client(require_openai_api_key())


def save_image_bytes(file_name, image_bytes):
    suffix = Path(file_name).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(image_bytes)
        return Path(temp_file.name)


def format_coordinate(value):
    if value is None:
        return None
    return round(value, 6)


def is_garbage(classification):
    return (classification or "").strip().lower().startswith("yes")


def build_image_record(uploaded_file, index):
    image_bytes = uploaded_file.getvalue()
    attributes = extract_image_attributes(image_bytes)

    return {
        "id": f"{index}-{uploaded_file.name}-{len(image_bytes)}",
        "file_name": uploaded_file.name,
        "format": attributes["format"],
        "size_kb": round(len(image_bytes) / 1024, 1),
        "width": attributes["width"],
        "height": attributes["height"],
        "latitude": format_coordinate(attributes["latitude"]),
        "longitude": format_coordinate(attributes["longitude"]),
        "classification": None,
        "alert_status": "Pending",
        "review_status": "Unreviewed",
        "notes": "",
        "image_bytes": image_bytes,
    }


def get_upload_signature(uploaded_files):
    return tuple((file.name, len(file.getvalue())) for file in uploaded_files)


def sync_uploaded_files(uploaded_files):
    signature = get_upload_signature(uploaded_files)
    if st.session_state.get("upload_signature") == signature:
        return

    st.session_state["upload_signature"] = signature
    st.session_state["records"] = [
        build_image_record(uploaded_file, index)
        for index, uploaded_file in enumerate(uploaded_files)
    ]
    st.session_state["selected_image_id"] = None


def classify_record(record):
    image_path = save_image_bytes(record["file_name"], record["image_bytes"])

    try:
        if USE_SIMULATED_PREDICTIONS:
            return classify_image_simulated(image_path)
        
        return classify_image_openai(
            client=get_client(),
            image_path=image_path,
            model=MODEL,
            prompt=CLASSIFICATION_PROMPT,
            detail=IMAGE_DETAIL,
        )
    finally:
        image_path.unlink(missing_ok=True)


def update_alert_status(record):
    if record["classification"] is None:
        record["alert_status"] = "Pending"
    elif record["classification"].startswith("Error:"):
        record["alert_status"] = "Error"
    elif is_garbage(record["classification"]) and record["latitude"] and record["longitude"]:
        record["alert_status"] = "New"
    elif is_garbage(record["classification"]):
        record["alert_status"] = "Missing GPS"
    else:
        record["alert_status"] = "No alert"


def get_results_dataframe(records):
    return pd.DataFrame([{key: record[key] for key in VISIBLE_COLUMNS} for record in records])


def get_alert_records(records):
    return [
        record
        for record in records
        if record["alert_status"] in {"New", "Reviewed", "Resolved", "Missing GPS"}
    ]


def get_marker_color(record):
    if record["alert_status"] == "Resolved":
        return [25, 135, 84, 190]
    if record["review_status"] == "Reviewed":
        return [255, 193, 7, 190]
    if record["alert_status"] == "New":
        return [220, 53, 69, 210]
    if record["alert_status"] == "Missing GPS":
        return [108, 117, 125, 190]
    return [13, 110, 253, 160]


def show_summary(records):
    processed = sum(record["classification"] is not None for record in records)
    garbage = sum(is_garbage(record["classification"]) for record in records)
    active_alerts = sum(record["alert_status"] == "New" for record in records)
    missing_gps = sum(record["latitude"] is None or record["longitude"] is None for record in records)

    columns = st.columns(4)
    columns[0].metric("Imagens", len(records))
    columns[1].metric("Processadas", processed)
    columns[2].metric("Alertas de lixo", active_alerts)
    columns[3].metric("Dados de GPS ausentes", missing_gps)

    if garbage and not active_alerts:
        st.info("Foi detectado lixo, mas nenhum alerta GPS ativo está disponível no momento.")


def show_results_table(records):
    widths = [2.3, 0.7, 0.8, 0.8, 0.8, 1.1, 1.1, 1.3, 1.1, 0.8]
    headers = [
        "File",
        "Format",
        "KB",
        "Width",
        "Height",
        "Latitude",
        "Longitude",
        "Result",
        "Alert",
        "Image",
    ]

    header_columns = st.columns(widths)
    for column, header in zip(header_columns, headers):
        column.markdown(f"**{header}**")

    for record in records:
        columns = st.columns(widths)
        columns[0].write(record["file_name"])
        columns[1].write(record["format"])
        columns[2].write(record["size_kb"])
        columns[3].write(record["width"])
        columns[4].write(record["height"])
        columns[5].write(record["latitude"])
        columns[6].write(record["longitude"])
        columns[7].write(record["classification"] or "-")
        columns[8].write(record["alert_status"])

        if columns[9].button("View", key=f"view-result-{record['id']}"):
            st.session_state["selected_image_id"] = record["id"]


def show_selected_image(records):
    selected_id = st.session_state.get("selected_image_id")
    if not selected_id:
        return

    selected_record = next(
        (record for record in records if record["id"] == selected_id),
        None,
    )
    if not selected_record:
        return

    st.image(
        selected_record["image_bytes"],
        caption=selected_record["file_name"],
        width="stretch",
    )


def show_alert_map(records):
    map_records = [
        record
        for record in records
        if record["latitude"] is not None
        and record["longitude"] is not None
        and record["alert_status"] in {"New", "Reviewed", "Resolved"}
    ]

    if not map_records:
        st.info("Os alertas de lixo serão exibidos no mapa.")
        return

    map_style_choice = st.radio(
        "Mapa",
        ["Claro", "Escuro"],
        horizontal=True,
        key="map_style_choice",
    )
    map_style = "light" if map_style_choice == "Claro" else "dark"

    map_rows = pd.DataFrame(
        [
            {
                "file_name": record["file_name"],
                "latitude": record["latitude"],
                "longitude": record["longitude"],
                "classification": record["classification"],
                "alert_status": record["alert_status"],
                "review_status": record["review_status"],
                "color": get_marker_color(record),
            }
            for record in map_records
        ]
    )
    view_state = pdk.ViewState(
        latitude=map_rows["latitude"].mean(),
        longitude=map_rows["longitude"].mean(),
        zoom=17,
        pitch=0,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_rows,
        get_position=["longitude", "latitude"],
        get_fill_color="color",
        get_radius=4,
        radius_min_pixels=9,
        radius_max_pixels=26,
        pickable=True,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": (
                    "<b>{file_name}</b><br/>"
                    "Alert: {alert_status}<br/>"
                    "Review: {review_status}<br/>"
                    "Result: {classification}<br/>"
                    "Lat: {latitude}<br/>"
                    "Lon: {longitude}"
                )
            },
        )
    )


def show_alert_list(records):
    alerts = get_alert_records(records)
    if not alerts:
        st.info("Sem alertas de lixo por enquanto. Classifique as imagens enviadas primeiro.")
        return

    for record in alerts:
        with st.container(border=True):
            columns = st.columns([1.2, 2, 1.2, 1.2])
            columns[0].image(record["image_bytes"], width="stretch")
            columns[1].markdown(f"**{record['file_name']}**")
            columns[1].write(f"Classification: {record['classification']}")
            columns[1].write(f"Location: {record['latitude']}, {record['longitude']}")
            columns[1].write(f"Notes: {record['notes'] or '-'}")
            columns[2].metric("Alert", record["alert_status"])
            columns[2].metric("Review", record["review_status"])

            if columns[3].button("Review", key=f"review-{record['id']}"):
                record["review_status"] = "Reviewed"
                if record["alert_status"] == "New":
                    record["alert_status"] = "Reviewed"
                st.rerun()

            if columns[3].button("Resolve", key=f"resolve-{record['id']}"):
                record["review_status"] = "Reviewed"
                record["alert_status"] = "Resolved"
                st.rerun()

            if columns[3].button("False positive", key=f"false-positive-{record['id']}"):
                record["review_status"] = "Reviewed"
                record["alert_status"] = "No alert"
                record["notes"] = "Marked false positive"
                st.rerun()


def classify_records(records):
    progress = st.progress(0)
    status = st.empty()

    for index, record in enumerate(records):
        status.write(f"Classifying {record['file_name']}")

        try:
            record["classification"] = classify_record(record)
        except Exception as exc:
            record["classification"] = f"Error: {exc}"

        update_alert_status(record)
        progress.progress((index + 1) / len(records))

    status.empty()


st.set_page_config(page_title="Siren", page_icon="S", layout="wide")
st.title("Siren Sky")

if "records" not in st.session_state:
    st.session_state["records"] = []
if "selected_image_id" not in st.session_state:
    st.session_state["selected_image_id"] = None

upload_tab, results_tab, alerts_tab = st.tabs(["Enviar", "Resultados", "Alertas"])

with upload_tab:
    uploaded_files = st.file_uploader(
        "Enviar imagens do drone para classificação",
        type=SUPPORTED_UPLOAD_TYPES,
        accept_multiple_files=True,
    )

    if uploaded_files:
        sync_uploaded_files(uploaded_files)

    records = st.session_state["records"]
    if records:
        show_summary(records)

        if st.button("Classificar imagens", type="primary"):
            classify_records(records)

        st.dataframe(get_results_dataframe(records), width="stretch", hide_index=True)

with results_tab:
    records = st.session_state["records"]
    if not records:
        st.info("Envie as imagens do drone primeiro.")
    else:
        show_summary(records)
        show_results_table(records)
        show_selected_image(records)

with alerts_tab:
    records = st.session_state["records"]
    if not records:
        st.info("Envie e classifique as imagens do drone primeiro.")
    else:
        show_summary(records)
        show_alert_map(records)
        show_alert_list(records)

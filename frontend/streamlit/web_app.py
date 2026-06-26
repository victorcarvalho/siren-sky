import sys
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.classification_service import DEFAULT_SETTINGS, classify_image_bytes
from backend.classifiers import create_openai_client
from backend.config import USE_SIMULATED_PREDICTIONS, require_openai_api_key
from backend.image_metadata import extract_image_attributes


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
        "alert_status": "Pendente",
        "review_status": "Não revisado",
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
    return classify_image_bytes(
        image_bytes=record["image_bytes"],
        filename=record["file_name"],
        client=get_client(),
        settings=DEFAULT_SETTINGS,
    )


def update_alert_status(record):
    if record["classification"] is None:
        record["alert_status"] = "Pendente"
    elif record["classification"].startswith("Error:"):
        record["alert_status"] = "Erro"
    elif is_garbage(record["classification"]) and record["latitude"] and record["longitude"]:
        record["alert_status"] = "Novo"
    elif is_garbage(record["classification"]):
        record["alert_status"] = "GPS ausente"
    else:
        record["alert_status"] = "Sem alerta"


def get_results_dataframe(records):
    return pd.DataFrame([{key: record[key] for key in VISIBLE_COLUMNS} for record in records])


def get_alert_records(records):
    return [
        record
        for record in records
        if record["alert_status"] in {"Novo", "Revisado", "Resolvido", "GPS ausente"}
    ]


def is_alert_record(record):
    return record["alert_status"] in {"Novo", "Revisado", "Resolvido", "GPS ausente"}


def get_marker_color(record):
    if record["alert_status"] == "Resolvido":
        return [25, 135, 84, 190]
    if record["review_status"] == "Revisado":
        return [255, 193, 7, 190]
    if record["alert_status"] == "Novo":
        return [220, 53, 69, 210]
    if record["alert_status"] == "GPS ausente":
        return [108, 117, 125, 190]
    return [13, 110, 253, 160]


def get_display_classification(classification):
    if classification is None or classification == "":
        return "-"
    if classification.startswith("Error:"):
        return classification
    if is_garbage(classification):
        return "Com lixo"
    else:
        return "Sem lixo"


def show_summary(records):
    processed = sum(record["classification"] is not None for record in records)
    garbage = sum(is_garbage(record["classification"]) for record in records)
    active_alerts = sum(record["alert_status"] == "Novo" for record in records)
    missing_gps = sum(record["latitude"] is None or record["longitude"] is None for record in records)

    columns = st.columns(4)
    columns[0].metric("Imagens", len(records))
    columns[1].metric("Processadas", processed)
    columns[2].metric("Dados de GPS ausentes", missing_gps)
    columns[3].metric("Alertas de lixo", active_alerts)

    if garbage and not active_alerts:
        st.info("Foi detectado lixo, mas nenhum alerta GPS ativo está disponível no momento.")


def show_results_table(records):
    widths = [2.3, 0.7, 0.8, 0.8, 0.8, 1.1, 1.1, 1.3, 1.1, 0.8]
    headers = [
        "Arquivo",
        # "Formato",
        "KB",
        "Largura",
        "Altura",
        "Latitude",
        "Longitude",
        "Classificação",
        "Alerta",
        "Imagem",
    ]

    header_columns = st.columns(widths)
    for column, header in zip(header_columns, headers):
        column.markdown(f"**{header}**")

    for record in records:
        columns = st.columns(widths)
        is_alert = is_alert_record(record)
        
        # Use markdown with red and bold styling for alert rows
        if is_alert:
            columns[0].markdown(f":red[**{record['file_name']}**]")
            columns[1].markdown(f":red[**{record['size_kb']}**]")
            columns[2].markdown(f":red[**{record['width']}**]")
            columns[3].markdown(f":red[**{record['height']}**]")
            columns[4].markdown(f":red[**{record['latitude']}**]")
            columns[5].markdown(f":red[**{record['longitude']}**]")
            columns[6].markdown(f":red[**{get_display_classification(record['classification'])}**]")
            columns[7].markdown(f":red[**{record['alert_status']}**]")
        else:
            columns[0].write(record["file_name"])
            columns[1].write(record["size_kb"])
            columns[2].write(record["width"])
            columns[3].write(record["height"])
            columns[4].write(record["latitude"])
            columns[5].write(record["longitude"])
            columns[6].write(get_display_classification(record["classification"]))
            columns[7].write(record["alert_status"])

        if columns[8].button("Visualizar", key=f"view-result-{record['id']}"):
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

    # Display modal popup
    @st.dialog("Visualizar imagem")
    def show_image_modal():
        classificaton = get_display_classification(selected_record["classification"])
        st.text(classificaton)
        st.image(
            selected_record["image_bytes"],
            caption=selected_record["file_name"],
            width="stretch",
        )
        if st.button("Fechar", key="close-image-modal"):
            st.session_state["selected_image_id"] = None
            st.rerun()
    
    show_image_modal()


def show_alert_map(records):
    map_records = [
        record
        for record in records
        if record["latitude"] is not None
        and record["longitude"] is not None
        and record["alert_status"] in {"Novo", "Revisado", "Resolvido"}
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
                "display_classification": get_display_classification(record["classification"]),
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
                    "Alerta: {alert_status}<br/>"
                    "Revisão: {review_status}<br/>"
                    "Resultado: {display_classification}<br/>"
                    "Lat: {latitude}<br/>"
                    "Lon: {longitude}"
                )
            },
        )
    )


def show_alert_list(records):
    alerts = get_alert_records(records)
    if not alerts:
        st.info("Sem alertas de lixo por enquanto. Classifique as imagens enviadas.")
        return

    for record in alerts:
        with st.container(border=True):
            columns = st.columns([1.2, 2, 1.2, 1.2])
            columns[0].image(record["image_bytes"], width="stretch")
            columns[1].markdown(f"**{record['file_name']}**")
            columns[1].write(f"Classificação: {get_display_classification(record['classification'])}")
            columns[1].write(f"Localização: {record['latitude']}, {record['longitude']}")
            columns[1].write(f"Notas: {record['notes'] or '-'}")
            columns[2].metric("Alerta", record["alert_status"])
            columns[2].metric("Revisão", record["review_status"])

            if columns[3].button("Revisar", key=f"review-{record['id']}"):
                record["review_status"] = "Revisado"
                if record["alert_status"] == "Novo":
                    record["alert_status"] = "Revisado"
                st.rerun()

            if columns[3].button("Resolver", key=f"resolve-{record['id']}"):
                record["review_status"] = "Revisado"
                record["alert_status"] = "Resolvido"
                st.rerun()


def classify_records(records):
    progress = st.progress(0)
    status = st.empty()

    for index, record in enumerate(records):
        status.write(f"Classificando {record['file_name']}")

        try:
            record["classification"] = classify_record(record)
        except Exception as exc:
            record["classification"] = f"Erro: {exc}"

        update_alert_status(record)
        progress.progress((index + 1) / len(records))

    status.empty()


st.set_page_config(
    page_title="Siren", 
    page_icon="S", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling matching the logo theme (dark blue, white, and light blue)
st.markdown("""
<style>
    /* Primary color scheme from logo */
    :root {
        --primary-dark: #003f7f;
        --primary-light: #0066cc;
        --accent-light: #87ceeb;
        --text-light: #ffffff;
        --text-dark: #003f7f;
        --border-color: #0066cc;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f0f7 100%);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #003f7f !important;
        font-weight: 700;
    }
    
    /* Title */
    .stTitle {
        color: #003f7f !important;
        text-shadow: 0 2px 4px rgba(0, 63, 127, 0.1);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] button {
        color: #003f7f;
        font-weight: 600;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: transparent !important;
        color: #0066cc;
    }
    
    .stTabs [aria-selected="true"] {
        color: #0066cc !important;
        background-color: transparent !important;
        border-bottom: 2px solid #0066cc !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #003f7f 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 6px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0052a3 0%, #003366 100%);
        box-shadow: 0 4px 8px rgba(0, 63, 127, 0.3);
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #0066cc 0%, #003f7f 100%) !important;
    }
    
    /* Metrics styling */
    .stMetric {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0, 63, 127, 0.1);
    }
    
    .stMetricLabel {
        color: #003f7f;
        font-weight: 600;
    }
    
    .stMetricValue {
        color: #0066cc;
        font-weight: 700;
    }
    
    /* Container borders */
    .stContainer {
        border-color: #0066cc !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #e8f0f7 !important;
        border-left: 4px solid #0066cc !important;
        color: #003f7f !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #0066cc !important;
    }
    
    .stDataFrame th {
        background-color: #003f7f !important;
        color: white !important;
        font-weight: 600;
    }
    
    /* Links */
    a {
        color: #0066cc !important;
    }
    
    a:hover {
        color: #003f7f !important;
    }
    
    /* Radio buttons */
    .stRadio {
        color: #003f7f;
    }
    
    .stRadio > label {
        font-weight: 500;
        color: #003f7f;
    }
    
    /* File uploader */
    .stFileUploader section {
        border: 2px dashed #0066cc;
        border-radius: 8px;
        background-color: #f8fbff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003f7f 0%, #0052a3 100%);
    }
    
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio {
        color: white;
    }
    
</style>
""", unsafe_allow_html=True)

st.title("🌊 SirenSky")

if "records" not in st.session_state:
    st.session_state["records"] = []
if "selected_image_id" not in st.session_state:
    st.session_state["selected_image_id"] = None

upload_results_tab, alerts_tab = st.tabs(["Enviar", "Alertas"])

with upload_results_tab:
    uploaded_files = st.file_uploader(
        "Enviar imagens do \"drone\" para classificação",
        type=SUPPORTED_UPLOAD_TYPES,
        accept_multiple_files=True,
        help="Faça upload de imagens capturadas pelo drone para detectar a presença de lixo."
    )

    if uploaded_files:
        sync_uploaded_files(uploaded_files)

    if st.session_state["records"]:
        if st.button("Classificar imagens", type="primary"):
            classify_records(st.session_state["records"])
    
    records = st.session_state["records"]
    if not records:
        st.info("Envie as imagens do \"drone\".")
    else:
        show_summary(records)
        show_results_table(records)
        show_selected_image(records)

with alerts_tab:
    records = st.session_state["records"]
    if not records:
        st.info("Envie e classifique as imagens do \"drone\".")
    else:
        show_summary(records)
        show_alert_map(records)
        show_alert_list(records)

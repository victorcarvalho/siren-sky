import sys
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also add the script's directory to sys.path for importing local modules like utils.py
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from backend.classification_service import DEFAULT_SETTINGS, classify_image_bytes
from backend.config import ALLOWED_EMAILS


from utils import (
    build_image_record,
    format_coordinate,
    get_alert_records,
    get_display_classification,
    get_marker_color,
    get_results_dataframe,
    get_upload_signature,
    is_alert_record,
    is_garbage,
    update_alert_status,
    get_status_badge_html,
)

from ui_templates import (
    show_empty_state,
    render_login_card,
    render_access_denied_card,
    render_model_footer,
)

SUPPORTED_UPLOAD_TYPES = ["jpg", "jpeg", "png", "webp"]


# Helper functions migrated to utils.py


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
        settings=DEFAULT_SETTINGS,
    )


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
        
        columns[0].write(record["file_name"])
        columns[1].write(record["size_kb"])
        columns[2].write(record["width"])
        columns[3].write(record["height"])
        columns[4].write(record["latitude"] if record["latitude"] is not None else "-")
        columns[5].write(record["longitude"] if record["longitude"] is not None else "-")
        columns[6].write(get_display_classification(record["classification"]))
        
        # Display the custom colored status pill badge
        columns[7].markdown(get_status_badge_html(record["alert_status"]), unsafe_allow_html=True)

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

    map_style = "light"

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
            columns[1].markdown(get_status_badge_html(record["alert_status"]), unsafe_allow_html=True)
            columns[1].write(f"Classificação: {get_display_classification(record['classification'])}")
            columns[1].write(f"Localização: {record['latitude'] or '-'}, {record['longitude'] or '-'}")
            
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
    page_title="SirenSky", 
    page_icon="favicon_io/favicon-32x32.png",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom CSS styling matching the logo theme (dark blue, white, and light blue)
css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Authentication check
if not st.user.is_logged_in:
    render_login_card()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Fazer Login com Google", type="primary", use_container_width=True):
            st.login()
            
    render_model_footer(DEFAULT_SETTINGS.model, margin_top="60px")
    st.stop()

# Email authorization check
allowed_emails_list = [email.strip() for email in ALLOWED_EMAILS.split(",") if email.strip()] if ALLOWED_EMAILS else []
if allowed_emails_list and st.user.email not in allowed_emails_list:
    render_access_denied_card(st.user.email)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sair / Entrar com outra conta", type="secondary", use_container_width=True):
            st.logout()
    st.stop()


# User profile and logout in sidebar
with st.sidebar:
    st.markdown("### 👤 Conta")
    user_name = st.user.name or "Usuário"
    st.write(f"**Nome:** {user_name}")
    st.write(f"**E-mail:** {st.user.email}")
    if st.button("Sair / Logout", type="secondary", use_container_width=True):
        st.logout()

st.title("SirenSky")

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
        show_empty_state()
    else:
        show_summary(records)
        show_results_table(records)
        show_selected_image(records)

with alerts_tab:
    records = st.session_state["records"]
    if not records:
        show_empty_state()
    else:
        # Alert tab filter controls
        st.markdown("### 🔍 Filtrar alertas")
        alerts_only = get_alert_records(records)
        if not alerts_only:
            st.info("Sem alertas de lixo por enquanto. Envie e classifique as imagens no painel principal.")
        else:
            available_statuses = sorted(list({r["alert_status"] for r in alerts_only}))
            selected_statuses = st.multiselect(
                "Filtrar por status do alerta:",
                options=available_statuses,
                default=available_statuses,
                key="alert_status_filter"
            )
            
            filtered_records = [r for r in records if r["alert_status"] in selected_statuses]
            
            if filtered_records:
                show_summary(filtered_records)
                show_alert_map(filtered_records)
                show_alert_list(filtered_records)
            else:
                st.warning("Nenhum alerta corresponde aos filtros selecionados.")


# Model configuration footer
render_model_footer(DEFAULT_SETTINGS.model, margin_top="40px")


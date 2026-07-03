import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.image_metadata import extract_image_attributes

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

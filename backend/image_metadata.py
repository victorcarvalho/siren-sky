from io import BytesIO

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


def _to_float(value):
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return value.numerator / value.denominator
    return float(value)


def _dms_to_decimal(dms, reference):
    degrees, minutes, seconds = (_to_float(part) for part in dms)
    decimal = degrees + minutes / 60 + seconds / 3600

    if reference in {"S", "W"}:
        decimal *= -1

    return decimal


def _get_gps_info(image):
    exif = image.getexif()
    if not exif:
        return None

    gps_tag_id = next(
        (tag_id for tag_id, name in TAGS.items() if name == "GPSInfo"),
        None,
    )
    if gps_tag_id is None:
        return None

    gps_ifd = exif.get_ifd(gps_tag_id)
    if not gps_ifd:
        return None

    return {GPSTAGS.get(tag_id, tag_id): value for tag_id, value in gps_ifd.items()}


def extract_gps_coordinates(image_bytes):
    with Image.open(BytesIO(image_bytes)) as image:
        gps_info = _get_gps_info(image)

    if not gps_info:
        return None

    latitude = gps_info.get("GPSLatitude")
    latitude_ref = gps_info.get("GPSLatitudeRef")
    longitude = gps_info.get("GPSLongitude")
    longitude_ref = gps_info.get("GPSLongitudeRef")

    if not all([latitude, latitude_ref, longitude, longitude_ref]):
        return None

    return {
        "latitude": _dms_to_decimal(latitude, latitude_ref),
        "longitude": _dms_to_decimal(longitude, longitude_ref),
    }


def extract_image_attributes(image_bytes):
    with Image.open(BytesIO(image_bytes)) as image:
        width, height = image.size
        image_format = image.format

    location = extract_gps_coordinates(image_bytes)

    return {
        "width": width,
        "height": height,
        "format": image_format,
        "latitude": location["latitude"] if location else None,
        "longitude": location["longitude"] if location else None,
    }

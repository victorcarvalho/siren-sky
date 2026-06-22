from fractions import Fraction

import image_metadata


def test_extract_image_attributes_returns_dimensions_and_format(image_file):
    image_path = image_file("sample.png", size=(32, 24))

    attributes = image_metadata.extract_image_attributes(image_path.read_bytes())

    assert attributes == {
        "width": 32,
        "height": 24,
        "format": "PNG",
        "latitude": None,
        "longitude": None,
    }


def test_dms_to_decimal_handles_direction():
    assert image_metadata._dms_to_decimal((Fraction(10, 1), Fraction(30, 1), Fraction(0, 1)), "N") == 10.5
    assert image_metadata._dms_to_decimal((Fraction(10, 1), Fraction(30, 1), Fraction(0, 1)), "W") == -10.5
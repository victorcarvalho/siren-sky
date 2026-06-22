import pytest
from PIL import Image


@pytest.fixture
def image_file(tmp_path):
    def _make_image(filename="sample.png", size=(16, 12), color=(12, 34, 56)):
        path = tmp_path / filename
        image = Image.new("RGB", size, color)
        image.save(path)
        return path

    return _make_image


@pytest.fixture
def dataset_root(tmp_path):
    root = tmp_path / "dataset"
    (root / "cats").mkdir(parents=True)
    (root / "dogs").mkdir(parents=True)
    return root
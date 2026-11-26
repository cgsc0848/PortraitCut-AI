from pathlib import Path
from PIL import Image
import pytest

from app.core.image_io import discover_images, load_rgb, save_rgba


def test_discover_supported_images(tmp_path: Path):
    (tmp_path / "a.jpg").write_bytes(b"placeholder")
    (tmp_path / "b.txt").write_text("not an image")
    (tmp_path / "c.PNG").write_bytes(b"placeholder")
    found = discover_images(tmp_path)
    assert [p.name for p in found] == ["a.jpg", "c.PNG"]


def test_save_rgba_preserves_rgb_and_alpha_size(tmp_path: Path):
    rgb = Image.new("RGB", (20, 10), (120, 30, 10))
    alpha = Image.new("L", (10, 5), 128)
    output = tmp_path / "result.png"
    save_rgba(rgb, alpha, output)
    with Image.open(output) as result:
        assert result.mode == "RGBA"
        assert result.size == (20, 10)
        assert result.getpixel((0, 0)) == (120, 30, 10, 128)


def test_load_rgb_rejects_image_over_pixel_guard(tmp_path: Path):
    path = tmp_path / "small.png"
    Image.new("RGB", (4, 4), "white").save(path)
    with pytest.raises(ValueError, match="limit is"):
        load_rgb(path, max_pixels=15)


def test_load_rgb_applies_exif_orientation(tmp_path: Path):
    path = tmp_path / "exif.jpg"
    image = Image.new("RGB", (30, 10), "blue")
    exif = image.getexif()
    exif[274] = 6
    image.save(path, exif=exif)
    loaded = load_rgb(path)
    assert loaded.size == (10, 30)

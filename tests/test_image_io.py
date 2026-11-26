from pathlib import Path
from PIL import Image

from app.core.image_io import discover_images, save_rgba


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

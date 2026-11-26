from __future__ import annotations

from pathlib import Path
from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def discover_images(folder: Path, recursive: bool = False) -> list[Path]:
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Input folder does not exist: {folder}")
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(
        p for p in iterator
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def load_rgb(path: Path) -> Image.Image:
    try:
        with Image.open(path) as source:
            source.load()
            return source.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Cannot read image '{path}': {exc}") from exc


def save_rgba(source_rgb: Image.Image, alpha: Image.Image, output_path: Path) -> None:
    source_rgb = source_rgb.convert("RGB")
    alpha = alpha.convert("L")
    if alpha.size != source_rgb.size:
        alpha = alpha.resize(source_rgb.size, Image.Resampling.LANCZOS)
    rgba = source_rgb.convert("RGBA")
    rgba.putalpha(alpha)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(output_path, format="PNG", optimize=True)

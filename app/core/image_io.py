from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
MAX_INPUT_PIXELS = 50_000_000
MAX_BATCH_FILES = 10_000


def discover_images(folder: Path, recursive: bool = False,
                    max_files: int = MAX_BATCH_FILES) -> list[Path]:
    folder = Path(folder).expanduser()
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Input folder does not exist: {folder}")
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    found = sorted(p for p in iterator
                   if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)
    if len(found) > max_files:
        raise ValueError(
            f"Batch contains {len(found):,} images; safety limit is {max_files:,}. "
            "Split the folder into smaller batches."
        )
    return found


def load_rgb(path: Path, max_pixels: int = MAX_INPUT_PIXELS) -> Image.Image:
    try:
        with Image.open(path) as source:
            width, height = source.size
            if width <= 0 or height <= 0 or width * height > max_pixels:
                raise ValueError(
                    f"Image is {width:,} × {height:,} ({width * height:,} pixels); "
                    f"limit is {max_pixels:,} pixels."
                )
            source.load()
            return ImageOps.exif_transpose(source).convert("RGB")
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

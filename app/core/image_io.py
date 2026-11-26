from __future__ import annotations

from itertools import islice
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
    if max_files < 1:
        raise ValueError("max_files must be at least 1")

    iterator = folder.rglob("*") if recursive else folder.iterdir()
    candidates = (
        path for path in iterator
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    # Stop as soon as the safety limit is exceeded. Sorting the entire tree
    # before checking the limit could consume unbounded time and memory.
    found = list(islice(candidates, max_files + 1))
    if len(found) > max_files:
        raise ValueError(
            f"Batch contains more than {max_files:,} images; "
            f"safety limit is {max_files:,}. Split the folder into smaller batches."
        )
    return sorted(found)


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

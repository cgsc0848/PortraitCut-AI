from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.core.image_io import discover_images, load_rgb, save_rgba
from app.core.matte import MatteEngine


@dataclass
class FileResult:
    source: Path
    output: Path | None
    success: bool
    message: str


@dataclass
class BatchReport:
    results: list[FileResult]

    @property
    def succeeded(self) -> int:
        return sum(item.success for item in self.results)

    @property
    def failed(self) -> int:
        return len(self.results) - self.succeeded


def run_batch(
    input_dir: Path,
    output_dir: Path,
    engine: MatteEngine,
    recursive: bool = False,
    refine_rgb: bool = False,
    progress: Callable[[int, int, FileResult], None] | None = None,
) -> BatchReport:
    input_dir = Path(input_dir).expanduser()
    output_dir = Path(output_dir).expanduser()
    input_resolved = input_dir.resolve()
    output_resolved = output_dir.resolve()
    if output_resolved == input_resolved or input_resolved in output_resolved.parents:
        raise ValueError("Output directory cannot be the input directory or a child of it")

    sources = discover_images(input_dir, recursive=recursive)
    results: list[FileResult] = []
    for index, source in enumerate(sources, start=1):
        try:
            rgb = load_rgb(source)
            prediction = engine.predict(rgb)
            final_rgb = rgb
            if refine_rgb:
                from app.engine.birefnet import refine_foreground_rgb
                final_rgb = refine_foreground_rgb(rgb, prediction.alpha)

            relative = source.resolve().relative_to(input_resolved)
            output = (output_dir / relative).with_suffix(".png")
            if output.exists():
                output = output.with_name(
                    f"{source.stem}__{source.suffix.lstrip('.').lower()}.png"
                )
            save_rgba(final_rgb, prediction.alpha, output)
            message = prediction.warning or (
                f"{prediction.model_name} @ {prediction.used_resolution}px"
            )
            result = FileResult(source, output, True, message)
        except Exception as exc:
            result = FileResult(source, None, False, f"{type(exc).__name__}: {exc}")
        results.append(result)
        if progress:
            progress(index, len(sources), result)
    return BatchReport(results)

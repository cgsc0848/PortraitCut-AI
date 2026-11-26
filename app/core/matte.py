from __future__ import annotations

from dataclasses import dataclass
from PIL import Image


@dataclass
class MatteResult:
    alpha: Image.Image
    model_name: str
    used_resolution: int
    warning: str | None = None


class MatteEngine:
    """Common interface for local AI matte engines."""

    name = "abstract"

    def predict(self, image: Image.Image) -> MatteResult:
        raise NotImplementedError

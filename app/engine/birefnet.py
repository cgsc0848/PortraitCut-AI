from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from PIL import Image

from app.core.matte import MatteEngine, MatteResult

MODEL_ID = "ZhengPeng7/BiRefNet_HR-matting"
MODEL_REVISION = "5d6b6f8adcb5b417c871b1d84ceaae9871355b7f"
DEFAULT_RESOLUTIONS = (2048, 1792, 1536, 1280, 1024)


@dataclass
class Runtime:
    torch: object
    transforms: object
    model: object
    device: str
    dtype: object


class BiRefNetHREngine(MatteEngine):
    """BiRefNet-HR adapter pinned to a reviewed upstream revision."""

    name = "BiRefNet-HR-matting"

    def __init__(self, resolutions: Iterable[int] = DEFAULT_RESOLUTIONS,
                 prefer_cuda: bool = True, cache_dir: str | None = None) -> None:
        self.resolutions = tuple(dict.fromkeys(int(x) for x in resolutions))
        if not self.resolutions or any(x < 256 or x > 2048 for x in self.resolutions):
            raise ValueError("Resolutions must be between 256 and 2048")
        self.prefer_cuda = prefer_cuda
        self.cache_dir = cache_dir
        self._runtime: Runtime | None = None

    def load(self) -> None:
        if self._runtime is not None:
            return
        try:
            import torch
            from torchvision import transforms
            from transformers import AutoModelForImageSegmentation
        except ImportError as exc:
            raise RuntimeError(
                "AI dependencies are missing. Install a matching PyTorch CUDA wheel, "
                "then install requirements-ai.txt."
            ) from exc

        if self.prefer_cuda and torch.cuda.is_available():
            device, dtype = "cuda", torch.float16
        else:
            device, dtype = "cpu", torch.float32

        kwargs = {
            "trust_remote_code": True,
            "revision": MODEL_REVISION,
            "use_safetensors": True,
        }
        if self.cache_dir:
            kwargs["cache_dir"] = self.cache_dir
        try:
            model = AutoModelForImageSegmentation.from_pretrained(MODEL_ID, **kwargs)
            model.to(device)
            model.eval()
            if dtype == torch.float16:
                model.half()
        except Exception as exc:
            raise RuntimeError(
                f"Could not load {MODEL_ID} at pinned revision {MODEL_REVISION}: {exc}"
            ) from exc

        self._runtime = Runtime(torch, transforms, model, device, dtype)

    def predict(self, image: Image.Image) -> MatteResult:
        self.load()
        assert self._runtime is not None
        rt = self._runtime
        rgb = image.convert("RGB")
        last_oom: Exception | None = None
        attempted: list[int] = []

        for resolution in self.resolutions:
            attempted.append(resolution)
            tensor = None
            try:
                preprocess = rt.transforms.Compose([
                    rt.transforms.Resize((resolution, resolution)),
                    rt.transforms.ToTensor(),
                    rt.transforms.Normalize(
                        [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                    ),
                ])
                tensor = preprocess(rgb).unsqueeze(0).to(
                    device=rt.device, dtype=rt.dtype
                )
                with rt.torch.inference_mode():
                    predictions = rt.model(tensor)
                    logits = (
                        predictions[-1]
                        if isinstance(predictions, (tuple, list))
                        else predictions
                    )
                    matte = logits.sigmoid()[0].squeeze().float().cpu().numpy()

                matte = np.nan_to_num(matte, nan=0.0, posinf=1.0, neginf=0.0)
                matte = np.clip(matte, 0.0, 1.0)
                alpha = Image.fromarray(
                    np.round(matte * 255).astype(np.uint8), mode="L"
                ).resize(rgb.size, Image.Resampling.LANCZOS)

                warning = None
                if resolution != 2048:
                    warning = (
                        f"Inference completed at {resolution}px; "
                        f"attempted resolutions: {attempted}"
                    )
                return MatteResult(alpha, self.name, resolution, warning)

            except Exception as exc:
                message = str(exc).lower()
                oom_type = (
                    getattr(rt.torch.cuda, "OutOfMemoryError", ())
                    if rt.device == "cuda" else ()
                )
                is_oom = (
                    (bool(oom_type) and isinstance(exc, oom_type))
                    or "out of memory" in message
                    or "cuda error: memory allocation" in message
                )
                if not is_oom or rt.device != "cuda":
                    raise RuntimeError(
                        f"BiRefNet inference failed at {resolution}px: {exc}"
                    ) from exc
                last_oom = exc
                del tensor
                rt.torch.cuda.empty_cache()

        raise RuntimeError(
            f"CUDA out of memory at all configured resolutions {attempted}. "
            "Close other GPU applications or lower the minimum resolution."
        ) from last_oom


def refine_foreground_rgb(image: Image.Image, alpha: Image.Image) -> Image.Image:
    """Optional edge-color decontamination; this modifies RGB near the matte edge."""
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "Install requirements-ai.txt to enable foreground refinement"
        ) from exc

    src = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    matte = np.asarray(alpha.convert("L"), dtype=np.float32) / 255.0
    a = matte[:, :, None]

    def estimate(img: np.ndarray, foreground: np.ndarray,
                 background: np.ndarray, alpha_3d: np.ndarray, radius: int):
        blurred_alpha = cv2.blur(alpha_3d, (radius, radius))
        blurred_fa = cv2.blur(foreground * alpha_3d, (radius, radius))
        blurred_f = blurred_fa / (blurred_alpha + 1e-5)
        blurred_b1a = cv2.blur(background * (1.0 - alpha_3d), (radius, radius))
        blurred_b = blurred_b1a / ((1.0 - blurred_alpha) + 1e-5)
        result = blurred_f + alpha_3d * (
            img - alpha_3d * blurred_f - (1.0 - alpha_3d) * blurred_b
        )
        return np.clip(result, 0.0, 1.0), blurred_b

    foreground, background = estimate(src, src, src, a, 90)
    foreground, _ = estimate(src, foreground, background, a, 6)
    return Image.fromarray(np.round(foreground * 255).astype(np.uint8), mode="RGB")

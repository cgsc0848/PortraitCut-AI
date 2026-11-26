# PortraitCut AI

Local-first Windows desktop software for batch portrait background removal using NVIDIA GPU acceleration.

**Status: MVP Alpha.** The desktop UI, batch pipeline, RGBA PNG export, and pinned BiRefNet-HR adapter are under active development. CUDA performance and visual quality still require validation on a Windows NVIDIA machine.

## Features

- PySide6 desktop application
- BiRefNet-HR-matting adapter with CUDA/FP16 preference
- Sequential batch processing to control VRAM usage
- JPG, JPEG, PNG, WebP, BMP, and TIFF input
- Transparent RGBA PNG output while preserving source RGB
- Per-file error isolation
- Legacy white-background algorithm retained under `legacy/white-bg-cutout`

## Windows setup

1. Install 64-bit Python 3.11.
2. Run `scripts\\install_windows.ps1` in PowerShell.
3. Install the PyTorch CUDA wheel matching your NVIDIA driver from https://pytorch.org/get-started/locally/
4. Activate the environment and install AI dependencies:
   ```powershell
   .\\.venv\\Scripts\\Activate.ps1
   python -m pip install -r requirements-ai.txt
   python -m app.main
   ```

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

## Model safety

The pinned BiRefNet model is loaded with `trust_remote_code=True`, which executes Python code from the pinned model revision. Review that upstream code before running it, especially on machines containing sensitive data. Model weights are not stored in this repository.

## Testing

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

CI tests do not replace CUDA and visual-quality tests on a physical NVIDIA GPU.

## Limitations

- MultiMatte is not yet integrated as a standalone inference backend.
- Brush-based manual matte editing and a full before/after preview are not implemented yet.
- No Windows installer has been released.
- Photoshop-level results are not guaranteed; challenging hair, translucent fabric, and low-contrast clothing need dataset-based evaluation.

## License

No root project license has been selected. The legacy white-background component retains its own upstream license. Third-party dependencies and model weights have separate license terms.

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment missing. Run scripts\install_windows.ps1 first."
}

& ".\.venv\Scripts\python.exe" -m pip install "pyinstaller>=6.22,<7"
if ($LASTEXITCODE -ne 0) { throw "Could not install PyInstaller." }

$PyInstallerArgs = @(
    "--clean", "--noconfirm", "--onedir", "--windowed",
    "--name", "PortraitCutAI",
    "--collect-all", "torch",
    "--collect-all", "torchvision",
    "--collect-all", "transformers",
    "--collect-all", "huggingface_hub",
    "--collect-all", "timm",
    "--collect-all", "safetensors",
    "--collect-all", "cv2",
    "--collect-all", "scipy",
    "--collect-all", "skimage",
    "--collect-all", "kornia",
    "--collect-all", "einops",
    "--collect-all", "PySide6",
    "--hidden-import", "app.ui.main_window",
    "--distpath", "dist",
    "app\main.py"
)

& ".\.venv\Scripts\pyinstaller.exe" @PyInstallerArgs
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

Write-Host "Build complete: .\dist\PortraitCutAI\PortraitCutAI.exe"
Write-Host "Keep the entire onedir folder together. Model weights download on first run."

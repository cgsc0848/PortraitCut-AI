$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher not found. Install 64-bit Python 3.11 first."
}

py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) {
    throw "Could not create the Python 3.11 virtual environment."
}

$Python = ".\.venv\Scripts\python.exe"
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

& $Python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Base UI dependencies installation failed." }

Write-Host "Installing PyTorch 2.5.1 + torchvision 0.20.1 with CUDA 12.1 wheels..."
& $Python -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
if ($LASTEXITCODE -ne 0) { throw "CUDA-enabled PyTorch installation failed." }

& $Python -m pip install -r requirements-ai.txt
if ($LASTEXITCODE -ne 0) { throw "AI/model dependencies installation failed." }

& $Python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Development dependencies installation failed." }

& $Python scripts\verify_gpu.py
if ($LASTEXITCODE -ne 0) { throw "GPU verification failed." }

Write-Host ""
Write-Host "Environment setup complete."
Write-Host "Launch app: .\.venv\Scripts\python.exe -m app.main"
Write-Host "Run tests:  .\.venv\Scripts\python.exe -m pytest -q"
Write-Host ""
Write-Host "The PyTorch wheel supplies the CUDA runtime. A separate CUDA Toolkit install is normally not required."

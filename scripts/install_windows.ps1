$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher not found. Install Python 3.11 x64 first."
}

py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Could not create Python 3.11 virtual environment." }

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host ""
Write-Host "Base desktop dependencies installed."
Write-Host "Install the matching CUDA PyTorch wheel from https://pytorch.org/get-started/locally/"
Write-Host "Then run: .\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt"
Write-Host "Activate: .\.venv\Scripts\Activate.ps1"
Write-Host "Launch:   python -m app.main"

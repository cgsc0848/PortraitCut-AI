$ErrorActionPreference = "Stop"
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run scripts\install_windows.ps1 first."
}
& ".\.venv\Scripts\python.exe" -m app.main
if ($LASTEXITCODE -ne 0) { throw "PortraitCut AI exited with an error." }

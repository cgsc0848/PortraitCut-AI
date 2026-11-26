$ErrorActionPreference = "Stop"
$Python = ".\\.venv\\Scripts\\python.exe"
if (-not (Test-Path $Python)) { throw "Virtual environment missing. Run scripts\\install_windows.ps1 first." }
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed. See pytest output above." }
Write-Host "All local CPU and offscreen GUI smoke tests passed."

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$dbPath = Join-Path $projectRoot "data\cis.sqlite3"
$url = "http://127.0.0.1:5000"

if (-not (Test-Path $venvPython)) {
    Write-Host "Python del venv non trovato: $venvPython" -ForegroundColor Red
    Write-Host "Crea prima il venv Windows ed esegui: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Set-Location $projectRoot

if (-not (Test-Path $dbPath)) {
    Write-Host "Database non trovato. Inizializzo $dbPath ..." -ForegroundColor Yellow
    & $venvPython "init_db.py"
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Host "Avvio CIS su $url" -ForegroundColor Green
Start-Process $url
& $venvPython "run.py"
exit $LASTEXITCODE

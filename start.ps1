# Enterprise AI Platform — PowerShell Start Script
# Starts backend and frontend in parallel using background jobs.
# Usage: .\start.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Ensure data directories exist
@("data\qdrant", "data\logs") | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

Write-Host ""
Write-Host "Starting Enterprise AI Platform..." -ForegroundColor Cyan
Write-Host ""

# Start backend in a new window
Write-Host "[1/2] Backend  → http://localhost:8000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "[2/2] Frontend → http://localhost:5173" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command",
    "Set-Location frontend; npm run dev" `
    -WindowStyle Normal

Write-Host ""
Write-Host "Both services starting in separate windows." -ForegroundColor Green
Write-Host ""
Write-Host "  API health : http://localhost:8000/health"
Write-Host "  UI         : http://localhost:5173"
Write-Host "  API docs   : http://localhost:8000/docs"
Write-Host "  Login      : admin / admin123"
Write-Host ""

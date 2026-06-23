# Enterprise AI Platform — Windows 11 Setup Script
# Run from the project root in PowerShell:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   .\setup.ps1

param(
    [switch]$SkipFrontend,
    [switch]$SkipPip
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Enterprise AI Platform — Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python version check ────────────────────────────────────────────────────
Write-Host "[1/5] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install Python 3.11 from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $pythonVersion" -ForegroundColor Green

# ── 2. Create .env from example ───────────────────────────────────────────────
Write-Host "[2/5] Setting up .env file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created .env from .env.example" -ForegroundColor Green
    Write-Host "  ACTION REQUIRED: Open .env and set ANTHROPIC_API_KEY" -ForegroundColor Magenta
} else {
    Write-Host "  .env already exists — skipping" -ForegroundColor Green
}

# ── 3. Create data directories ────────────────────────────────────────────────
Write-Host "[3/5] Creating data directories..." -ForegroundColor Yellow
$dirs = @("data\qdrant", "data\seeds\insurance_claims", "data\seeds\banking",
          "data\seeds\manufacturing", "data\seeds\retail", "data\logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# ── 4. Python dependencies ────────────────────────────────────────────────────
if (-not $SkipPip) {
    Write-Host "[4/5] Installing Python dependencies..." -ForegroundColor Yellow
    Write-Host "  This may take 3-5 minutes on first run (downloading ML models)." -ForegroundColor Gray
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pip install failed. Check the error above." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Python dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[4/5] Skipping pip install (--SkipPip)" -ForegroundColor Gray
}

# ── 5. Frontend dependencies ───────────────────────────────────────────────────
if (-not $SkipFrontend) {
    Write-Host "[5/5] Installing frontend dependencies..." -ForegroundColor Yellow
    if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
        Write-Host "  WARNING: Node.js not found. Install from https://nodejs.org" -ForegroundColor Magenta
        Write-Host "  Skipping frontend setup." -ForegroundColor Gray
    } else {
        Push-Location frontend
        npm install --silent
        Pop-Location
        Write-Host "  Frontend dependencies installed." -ForegroundColor Green
    }
} else {
    Write-Host "[5/5] Skipping frontend install (--SkipFrontend)" -ForegroundColor Gray
}

# ── Done ───────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and set your ANTHROPIC_API_KEY"
Write-Host "  2. Run:  .\start.bat              (starts API + UI)"
Write-Host "  3. Open: http://localhost:5173"
Write-Host "  4. Login: admin / admin123"
Write-Host ""
Write-Host "Hackathon bootstrap (when you have a use case document):"
Write-Host "  Paste the problem statement into data\usecase.md"
Write-Host "  Run: python scripts\bootstrap_from_usecase.py"
Write-Host ""

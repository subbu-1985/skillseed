# SkillSeed - Run Both Backend and Frontend

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  SkillSeed - Start All Services" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend in a new terminal window
Write-Host "[1/2] Starting FastAPI Backend on port 8000..." -ForegroundColor Yellow
$backendCommand = "cd '$PSScriptRoot'; if (Test-Path 'venv\Scripts\activate.ps1') { .\venv\Scripts\activate.ps1 } else { Write-Host 'Virtual env not found, trying without it...' }; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Give backend a couple of seconds to start
Write-Host "Waiting 3 seconds for backend to initialize..." -ForegroundColor DarkGray
Start-Sleep -Seconds 3

# Start Frontend in a new terminal window
Write-Host "[2/2] Starting Flutter Frontend in Chrome..." -ForegroundColor Yellow
$frontendCommand = "cd '$PSScriptRoot\frontend'; flutter run -d chrome"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host ""
Write-Host "✅ Both services are starting up!" -ForegroundColor Green
Write-Host " - The backend will run on http://localhost:8000"
Write-Host " - The frontend will open in a new Chrome window"
Write-Host ""
Write-Host "You can close this window now. The services are running in their own windows."

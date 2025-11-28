$ErrorActionPreference = "Stop"

$root = Get-Location
$servicesDir = Join-Path $root "services"
$gatewayDir = Join-Path $root "gateway"
$venvActivate = Join-Path $root "Scripts\activate.ps1"

# Check if venv exists
if (-not (Test-Path $venvActivate)) {
    Write-Warning "Virtual environment activation script not found at $venvActivate. Trying standard location..."
    # Fallback check
    $venvActivate = Join-Path $root "venv\Scripts\activate.ps1"
}

Write-Host "" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Eventos Peru - Microservices Startup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "Using Virtual Env: $venvActivate" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan

# Start microservices
Write-Host "Starting microservices from $servicesDir..." -ForegroundColor Yellow

$services = Get-ChildItem -Path $servicesDir -Directory

foreach ($service in $services) {
    $runBat = Join-Path $service.FullName "run.bat"
    if (Test-Path $runBat) {
        Write-Host "  [+] Starting $($service.Name)..." -ForegroundColor Green
        
        # Command explanation:
        # 1. . $venvActivate  -> Dotsource the activation script to activate the env in the current scope
        # 2. & $runBat        -> Execute the batch file (which inherits the activated env)
        $command = ". '$venvActivate'; & '$runBat'"
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "$command"
        Start-Sleep -Milliseconds 500  # Small delay between services
    } else {
        Write-Host "  [-] Skipping $($service.Name) (run.bat not found)" -ForegroundColor Yellow
    }
}

# Start API Gateway
Write-Host "" -ForegroundColor Cyan
Write-Host "Starting API Gateway on port 8000..." -ForegroundColor Yellow
$gatewayRunBat = Join-Path $gatewayDir "run.bat"
if (Test-Path $gatewayRunBat) {
    Write-Host "  [+] Starting API Gateway..." -ForegroundColor Green
    $command = ". '$venvActivate'; & '$gatewayRunBat'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$command"
} else {
    Write-Host "  [-] Gateway run.bat not found at $gatewayRunBat" -ForegroundColor Red
}

Write-Host "" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  All services started!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "Service Ports:" -ForegroundColor White
Write-Host "  - API Gateway:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - IAM Service:     http://localhost:8010" -ForegroundColor Gray
Write-Host "  - Catalogo:        http://localhost:8020" -ForegroundColor Gray
Write-Host "  - Proveedores:     http://localhost:8030" -ForegroundColor Gray
Write-Host "  - Contratacion:    http://localhost:8040" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "Frontend should connect to: http://localhost:8000" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

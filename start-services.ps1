$ErrorActionPreference = "Stop"

$root = Get-Location
$servicesDir = Join-Path $root "services"
$venvActivate = Join-Path $root "Scripts\activate.ps1"

# Check if venv exists
if (-not (Test-Path $venvActivate)) {
    Write-Warning "Virtual environment activation script not found at $venvActivate. Trying standard location..."
    # Fallback check
    $venvActivate = Join-Path $root "venv\Scripts\activate.ps1"
}

Write-Host "Starting all services from $servicesDir..." -ForegroundColor Cyan
Write-Host "Using Virtual Env: $venvActivate" -ForegroundColor Gray

$services = Get-ChildItem -Path $servicesDir -Directory

foreach ($service in $services) {
    $runBat = Join-Path $service.FullName "run.bat"
    if (Test-Path $runBat) {
        Write-Host "Starting $($service.Name)..." -ForegroundColor Green
        
        # Command explanation:
        # 1. . $venvActivate  -> Dotsource the activation script to activate the env in the current scope
        # 2. & $runBat        -> Execute the batch file (which inherits the activated env)
        $command = ". '$venvActivate'; & '$runBat'"
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "$command"
    } else {
        Write-Host "Skipping $($service.Name) (run.bat not found)" -ForegroundColor Yellow
    }
}

Write-Host "All services started." -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$pidsPath = Join-Path $here ".run\pids.json"
if (-not (Test-Path $pidsPath)) {
    Write-Host "No hay .run\pids.json" -ForegroundColor Yellow
    exit 0
}

# stop-all.ps1 (reemplaza el bucle por este bloque)
Write-Host "Deteniendo procesos Python asociados a microservicios..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*eventos-peru-hexagonal*"
} | ForEach-Object {
    Write-Host "→ Matando $_.Id ($($_.Path))" -ForegroundColor Red
    Stop-Process -Id $_.Id -Force
}
Write-Host "Todos los servicios detenidos." -ForegroundColor Green


Write-Host "Listo."

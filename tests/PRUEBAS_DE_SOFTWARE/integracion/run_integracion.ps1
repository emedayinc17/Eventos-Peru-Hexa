# Ejecuta pruebas de integración (requieren servicios y fixtures)
# Uso:
#   .\tests\PRUEBAS_DE_SOFTWARE\integracion\run_integracion.ps1

param(
    [string]$Python = "python",
    [string]$ApiBase = $env:API_BASE
)

if (-not $ApiBase) {
    Write-Host "API_BASE no configurado. Usando http://localhost:8000" -ForegroundColor Yellow
    $env:API_BASE = "http://localhost:8000"
}

Write-Host "Ejecutando pruebas de integración contra $env:API_BASE"
& $Python -m pytest tests/PRUEBAS_DE_SOFTWARE/integracion -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Algunas pruebas de integración fallaron (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Pruebas de integración completadas correctamente" -ForegroundColor Green

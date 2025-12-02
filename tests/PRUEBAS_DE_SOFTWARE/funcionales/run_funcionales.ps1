# Ejecuta las pruebas funcionales
# Requiere servicios levantados (IAM, gateway, catalogo, contratacion...)
# Uso:
#   Set-Location e:\eventos-peru-hexagonal
#   .\tests\PRUEBAS_DE_SOFTWARE\funcionales\run_funcionales.ps1 -Python python

param(
    [string]$Python = "python",
    [string]$ApiBase = $env:API_BASE
)

if (-not $ApiBase) {
    Write-Host "API_BASE no configurado. Usando http://localhost:8000" -ForegroundColor Yellow
    $env:API_BASE = "http://localhost:8000"
}

Write-Host "Ejecutando tests funcionales contra $env:API_BASE"
& $Python -m pytest tests/PRUEBAS_DE_SOFTWARE/funcionales -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Algunas pruebas funcionales fallaron (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Pruebas funcionales completadas correctamente" -ForegroundColor Green

# Ejecuta tests de rendimiento con k6 (si está instalado)
# Uso:
#   .\tests\PRUEBAS_DE_SOFTWARE\rendimiento\run_k6.ps1 [-Script load_test_k6.js] [-ApiBase http://localhost:8000]

param(
    [string]$Script = "load_test_k6.js",
    [string]$ApiBase = $env:API_BASE
)

if (-not $ApiBase) {
    Write-Host "API_BASE no configurado. Usando http://localhost:8000" -ForegroundColor Yellow
    $ApiBase = "http://localhost:8000"
}

if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
    Write-Host "k6 no está instalado o no está en PATH. Instale k6 antes de ejecutar esta tarea." -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando k6 script: $Script contra $ApiBase"
$env:API_BASE = $ApiBase
k6 run .\tests\PRUEBAS_DE_SOFTWARE\rendimiento\$Script
if ($LASTEXITCODE -ne 0) {
    Write-Host "k6 reportó errores (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "k6 completado correctamente" -ForegroundColor Green

# Ejecuta todas las pruebas de seguridad (unitarias/integ/pentesting/analisis)
# Uso: abrir PowerShell en la raíz del repo y ejecutar:
#   .\tests\PRUEBAS_DE_SEGURIDAD\run_security.ps1

param(
    [string]$Python = "python",
    [string]$ApiBase = $env:API_BASE,
    [switch]$RunBandit,
    [switch]$RunTrivy
)

if (-not $ApiBase) {
    Write-Host "API_BASE no configurado. Usando http://localhost:8000" -ForegroundColor Yellow
    $env:API_BASE = "http://localhost:8000"
}

# Ejecutar pytest en la carpeta de seguridad
Write-Host "Ejecutando pruebas de seguridad (pytest) contra $env:API_BASE"
& $Python -m pytest tests/PRUEBAS_DE_SEGURIDAD -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Algunas pruebas de seguridad fallaron (exit code: $LASTEXITCODE)" -ForegroundColor Red
} else {
    Write-Host "Pruebas de seguridad completadas" -ForegroundColor Green
}

# Opcional: ejecutar bandit/trivy si se solicitan
if ($RunBandit) {
    Write-Host "Ejecutando Bandit..."
    & bash -c "./tests/PRUEBAS_DE_SEGURIDAD/analisis_vulnerabilidades/bandit_run.sh"
}

if ($RunTrivy) {
    Write-Host "Ejecutando Trivy (requiere parámetro -Image)
Uso: .\tests\PRUEBAS_DE_SEGURIDAD\run_security.ps1 -RunTrivy -Image 'my-image:tag'"
}

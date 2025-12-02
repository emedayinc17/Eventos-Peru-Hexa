# Ejecuta solo las pruebas unitarias del proyecto
# Uso: abrir PowerShell en la raiz del repo y ejecutar:
#   .\tests\PRUEBAS_DE_SOFTWARE\unitarias\run_unitarias.ps1

param(
    [string]$Python = "python",
    [switch]$InstallDeps
)

if ($InstallDeps) {
    Write-Host "Instalando dependencias desde requirements.txt..."
    & $Python -m pip install -r requirements.txt
}

Write-Host "Ejecutando tests unitarios (pytest) en tests/PRUEBAS_DE_SOFTWARE/unitarias"
& $Python -m pytest tests/PRUEBAS_DE_SOFTWARE/unitarias -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Algunos tests unitarios fallaron (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Tests unitarios completados correctamente" -ForegroundColor Green

# Script de Ejecución de Tests - Eventos Perú
# Ejecutar: .\run-tests.ps1 [tipo]
# Ejemplos:
#   .\run-tests.ps1           # Todos los tests
#   .\run-tests.ps1 integration
#   .\run-tests.ps1 e2e
#   .\run-tests.ps1 security

param(
    [Parameter(Position=0)]
    [ValidateSet('all', 'unit', 'integration', 'e2e', 'security', 'quick', 'coverage')]
    [string]$TestType = 'all'
)

# Colores
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Cyan = [ConsoleColor]::Cyan
$Red = [ConsoleColor]::Red

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════════" -ForegroundColor $Cyan
Write-Host "   EVENTOS PERÚ - TEST RUNNER" -ForegroundColor $Cyan
Write-Host "══════════════════════════════════════════════════════════════════" -ForegroundColor $Cyan
Write-Host ""

# Verificar que pytest está instalado
try {
    $null = Get-Command pytest -ErrorAction Stop
    Write-Host "✅ pytest encontrado" -ForegroundColor $Green
} catch {
    Write-Host "❌ pytest no encontrado. Instalando..." -ForegroundColor $Red
    pip install pytest pytest-html pytest-cov
}

# Definir comando según tipo de test
$command = ""
switch ($TestType) {
    'all' {
        Write-Host "🚀 Ejecutando TODOS los tests..." -ForegroundColor $Yellow
        $command = "pytest tests/ -v --tb=short"
    }
    'unit' {
        Write-Host "🔬 Ejecutando tests UNITARIOS..." -ForegroundColor $Yellow
        $command = "pytest tests/unit/ -v -m unit"
    }
    'integration' {
        Write-Host "🔗 Ejecutando tests de INTEGRACIÓN..." -ForegroundColor $Yellow
        $command = "pytest tests/integration/ -v -m integration"
    }
    'e2e' {
        Write-Host "🌐 Ejecutando tests END-TO-END..." -ForegroundColor $Yellow
        $command = "pytest tests/e2e/ -v -m e2e"
    }
    'security' {
        Write-Host "🔐 Ejecutando tests de SEGURIDAD..." -ForegroundColor $Yellow
        $command = "pytest tests/security/ -v -m security"
    }
    'quick' {
        Write-Host "⚡ Ejecutando tests RÁPIDOS (sin slow)..." -ForegroundColor $Yellow
        $command = "pytest tests/ -v -m 'not slow'"
    }
    'coverage' {
        Write-Host "📊 Ejecutando tests con COBERTURA..." -ForegroundColor $Yellow
        $command = "pytest tests/ -v --cov=services --cov-report=html --cov-report=term"
    }
}

Write-Host ""
Write-Host "Comando: $command" -ForegroundColor $Cyan
Write-Host ""

# Ejecutar tests
$startTime = Get-Date
Invoke-Expression $command
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════════" -ForegroundColor $Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ TESTS COMPLETADOS EXITOSAMENTE" -ForegroundColor $Green
} else {
    Write-Host "❌ TESTS FALLARON (Exit Code: $exitCode)" -ForegroundColor $Red
}

Write-Host "⏱️  Tiempo total: $([math]::Round($duration, 2)) segundos" -ForegroundColor $Yellow
Write-Host "══════════════════════════════════════════════════════════════════" -ForegroundColor $Cyan
Write-Host ""

# Generar reporte HTML si fue exitoso y no es coverage
if ($exitCode -eq 0 -and $TestType -ne 'coverage') {
    Write-Host "📄 ¿Generar reporte HTML? (s/n): " -NoNewline -ForegroundColor $Yellow
    $response = Read-Host
    if ($response -eq 's') {
        $reportName = "report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
        Write-Host "Generando reporte HTML..." -ForegroundColor $Cyan
        pytest tests/ --html="tests/reports/$reportName" --self-contained-html
        Write-Host "✅ Reporte generado: tests/reports/$reportName" -ForegroundColor $Green
        
        Write-Host "¿Abrir reporte? (s/n): " -NoNewline -ForegroundColor $Yellow
        $openReport = Read-Host
        if ($openReport -eq 's') {
            Start-Process "tests/reports/$reportName"
        }
    }
}

# Abrir reporte de cobertura si se generó
if ($TestType -eq 'coverage') {
    Write-Host ""
    Write-Host "¿Abrir reporte de cobertura? (s/n): " -NoNewline -ForegroundColor $Yellow
    $openCov = Read-Host
    if ($openCov -eq 's') {
        Start-Process "htmlcov/index.html"
    }
}

exit $exitCode

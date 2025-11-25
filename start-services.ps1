<#
Start all local microservices for the Eventos Perú workspace.
Opens a separate PowerShell window per service and runs uvicorn with the service's .env.
No Docker is used.
#>

Write-Host "Iniciando microservicios locales (sin Docker)" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Start-Service-Window {
    param (
        [string]$Name,
        [int]$Port,
        [string]$Path
    )

    $pythonPath = "${rootPath}\libs\shared;${rootPath};${rootPath}\services\$Name"
    
    $cmd = @"
`$host.UI.RawUI.WindowTitle = '$Name ($Port)'
Write-Host 'Iniciando $Name en puerto $Port...' -ForegroundColor Cyan

# Activar entorno virtual si existe en la raíz del repo
if (Test-Path "${rootPath}\Scripts\Activate.ps1") {
    try {
        . "${rootPath}\Scripts\Activate.ps1"
        Write-Host 'Entorno virtual activado' -ForegroundColor Green
    } catch {
        Write-Warning "No se pudo activar el entorno virtual: `$_"
    }
}

# Ajustar PYTHONPATH para resolver libs compartidas
`$env:PYTHONPATH = '$pythonPath'

cd '$Path'

# Asegurar .env
if (-Not (Test-Path '.env')) {
    if (Test-Path '.env.example') {
        Copy-Item '.env.example' '.env' -Force
        Write-Host '.env creado a partir de .env.example' -ForegroundColor Yellow
    } else {
        Write-Warning 'No se encontro .env ni .env.example; verifica configuracion.'
    }
} else {
    Write-Host '.env encontrado' -ForegroundColor Green
}

# Ejecutar uvicorn usando entrypoint estándar del proyecto
python -m uvicorn app.entrypoints.fastapi.main:app --host 0.0.0.0 --port $Port --env-file .env
"@

    Start-Process powershell -ArgumentList @('-NoExit','-Command', $cmd) -WindowStyle Normal
}

# Servicios a iniciar (ajusta paths/puertos si es necesario)
Start-Service-Window -Name 'iam-service' -Port 8010 -Path "${rootPath}\services\iam-service"
Start-Sleep -Milliseconds 300
Start-Service-Window -Name 'catalogo-service' -Port 8020 -Path "${rootPath}\services\catalogo-service"
Start-Sleep -Milliseconds 300
Start-Service-Window -Name 'proveedores-service' -Port 8030 -Path "${rootPath}\services\proveedores-service"
Start-Sleep -Milliseconds 300
Start-Service-Window -Name 'contratacion-service' -Port 8040 -Path "${rootPath}\services\contratacion-service"

Write-Host "------------------------------------------------------------"
Write-Host "Comandos de inicio emitidos. Revisa las ventanas abiertas para logs." -ForegroundColor Cyan
Write-Host "Para ejecutar: powershell -NoProfile -ExecutionPolicy Bypass -File start-services.ps1" -ForegroundColor Yellow

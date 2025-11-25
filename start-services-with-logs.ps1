# Script para iniciar todos los servicios y capturar logs
# Ejecuta cada servicio en background y muestra logs en consola

Write-Host "[INICIO] Iniciando todos los servicios..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"

$rootPath = "e:\eventos-peru-hexagonal"

# Activar entorno virtual
if (Test-Path "$rootPath\Scripts\Activate.ps1") {
    . "$rootPath\Scripts\Activate.ps1"
    Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
}

# Configurar PYTHONPATH
$env:PYTHONPATH = "$rootPath\libs\shared;$rootPath"

# Función para iniciar servicio en background
function Start-ServiceBackground {
    param (
        [string]$Name,
        [int]$Port,
        [string]$Path
    )
    
    Write-Host "Iniciando $Name en puerto $Port..." -ForegroundColor Yellow
    
    $job = Start-Job -ScriptBlock {
        param($servicePath, $port, $pythonPath)
        
        $env:PYTHONPATH = $pythonPath
        Set-Location $servicePath
        
        python -m uvicorn app.entrypoints.fastapi.main:app --host 0.0.0.0 --port $port --env-file .env 2>&1
    } -ArgumentList $Path, $Port, $env:PYTHONPATH -Name $Name
    
    return $job
}

# Iniciar servicios
$jobs = @()
$jobs += Start-ServiceBackground -Name 'iam-service' -Port 8010 -Path "$rootPath\services\iam-service"
Start-Sleep -Seconds 2

$jobs += Start-ServiceBackground -Name 'catalogo-service' -Port 8020 -Path "$rootPath\services\catalogo-service"
Start-Sleep -Seconds 2

$jobs += Start-ServiceBackground -Name 'proveedores-service' -Port 8030 -Path "$rootPath\services\proveedores-service"
Start-Sleep -Seconds 2

$jobs += Start-ServiceBackground -Name 'contratacion-service' -Port 8040 -Path "$rootPath\services\contratacion-service"

Write-Host ""
Write-Host "[OK] Todos los servicios iniciados" -ForegroundColor Green
Write-Host "Esperando 5 segundos para que los servicios arranquen..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "[LOGS] LOGS DE SERVICIOS:" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"

# Mostrar logs de cada servicio
foreach ($job in $jobs) {
    Write-Host ""
    Write-Host "=== $($job.Name) ===" -ForegroundColor Magenta
    $output = Receive-Job -Job $job
    if ($output) {
        $output | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "Sin logs aun..." -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host "Presiona Ctrl+C para detener todos los servicios" -ForegroundColor Yellow
Write-Host "Los servicios estan corriendo en background (Job IDs: $($jobs.Id -join ', '))"

# Mantener el script corriendo y mostrar logs continuamente
try {
    while ($true) {
        Start-Sleep -Seconds 3
        
        foreach ($job in $jobs) {
            $newOutput = Receive-Job -Job $job
            if ($newOutput) {
                Write-Host ""
                Write-Host "[$($job.Name)]" -ForegroundColor Cyan -NoNewline
                Write-Host " $newOutput"
            }
        }
    }
} finally {
    Write-Host ""
    Write-Host "[STOP] Deteniendo servicios..." -ForegroundColor Red
    $jobs | Stop-Job
    $jobs | Remove-Job
    Write-Host "[OK] Servicios detenidos" -ForegroundColor Green
}

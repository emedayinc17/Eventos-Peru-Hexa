$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$services = @(
    @{ name="iam-service";          path="services\iam-service" },
    @{ name="catalogo-service";     path="services\catalogo-service" },
    @{ name="proveedores-service";  path="services\proveedores-service" },
    @{ name="contratacion-service"; path="services\contratacion-service" }
)

$runDir = Join-Path $here ".run"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$pids = @()

foreach ($svc in $services) {
    $svcName = $svc.name
    $svcPath = Join-Path $here $svc.path
    $runFile = Join-Path $svcPath "run.bat"
    if (-not (Test-Path $runFile)) {
        Write-Host "[skip] $svcName no existe $runFile" -ForegroundColor Yellow
        continue
    }

    $svcRunDir = Join-Path $svcPath ".run"
    New-Item -ItemType Directory -Force -Path $svcRunDir | Out-Null
    $outLog = Join-Path $svcRunDir "out.log"
    $errLog = Join-Path $svcRunDir "err.log"

    Write-Host "[start] $svcName"

    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "`"$runFile`"" `
        -WorkingDirectory $svcPath `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $outLog `
        -RedirectStandardError $errLog

    $pids += @(@{ name=$svcName; pid=$proc.Id; path=$svcPath; out=$outLog; err=$errLog })
}

$pidsPath = Join-Path $runDir "pids.json"
$pids | ConvertTo-Json | Set-Content -Path $pidsPath -Encoding utf8

Write-Host ""
Write-Host "PIDs guardados en: $pidsPath"
Write-Host "Tips:"
Write-Host "  Get-Content -Tail 100 -Wait services\<svc>\.run\out.log" -ForegroundColor DarkGray

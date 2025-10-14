# created by emeday 2025 — robust run.ps1 (PS5/PS7 compatible)
Param(
    [string]$EnvFile = ".env"
)
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Get-DotEnv {
    param([string]$Path)
    $map = @{}
    if (Test-Path $Path) {
        Get-Content -Path $Path | ForEach-Object {
            $line = $_.Trim()
            if (-not $line) { return }
            if ($line.StartsWith("#")) { return }
            $idx = $line.IndexOf("=")
            if ($idx -gt 0) {
                $k = $line.Substring(0, $idx).Trim()
                $v = $line.Substring($idx+1).Trim()
                if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
                    $v = $v.Substring(1, $v.Length-2)
                }
                $map[$k] = $v
                [System.Environment]::SetEnvironmentVariable($k, $v, "Process")
            }
        }
    }
    return $map
}

$cfg = Get-DotEnv -Path $EnvFile

$svcName = if ($cfg.ContainsKey("SERVICE_NAME")) { $cfg["SERVICE_NAME"] } else { "service" }
$svcHost = if ($cfg.ContainsKey("HOST")) { $cfg["HOST"] } else { "0.0.0.0" }
try { $svcPort = if ($cfg.ContainsKey("PORT")) { [int]$cfg["PORT"] } else { 8000 } } catch { $svcPort = 8000 }

Write-Host ("[run] {0} on {1}:{2}" -f $svcName, $svcHost, $svcPort)

$modulePath = "app.entrypoints.fastapi.main:app"

$uvicornArgs = @(
    $modulePath,
    "--host", $svcHost,
    "--port", "$svcPort",
    "--env-file", $EnvFile
)

python -m uvicorn @uvicornArgs

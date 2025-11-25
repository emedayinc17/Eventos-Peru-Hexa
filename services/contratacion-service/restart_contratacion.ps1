$p = Get-NetTCPConnection -LocalPort 8040 -ErrorAction SilentlyContinue
if ($p) {
    $pid = $p.OwningProcess
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "Killed PID $pid on port 8040"
} else {
    Write-Host "No process on port 8040"
}
Start-Sleep -Seconds 1
Start-Process -FilePath 'e:\eventos-peru-hexagonal\services\contratacion-service\run.bat' -WorkingDirectory 'e:\eventos-peru-hexagonal\services\contratacion-service' -WindowStyle Normal
Write-Host 'Started contratacion-service'

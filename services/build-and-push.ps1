<#
.SYNOPSIS
  Build and optionally push Docker images for all services under `services/`.

.DESCRIPTION
  This script discovers service folders matching "*-service" inside the repository `services/`
  directory, builds Docker images using the repository root as build context (so shared libs are
  included), tags images prefixed with DockerHub user `emeday17/` and the provided tag,
  and optionally pushes them to DockerHub.

.PARAMETER Tag
  The image tag to apply to built images. Default: "1".

.PARAMETER Push
  If present, the script will `docker push` each built image after a successful build.

.PARAMETER Services
  Optional explicit list of service folder names to build (example: `iam-service`,`catalogo-service`).
  If omitted, the script will auto-detect folders under `services/` that match `*-service`.

.EXAMPLE
  # Build images with default tag (1) (no push)
  .\build-and-push.ps1

  # Build and push images with tag "1"
  .\build-and-push.ps1 -Push

  # Build only specific services and push
  .\build-and-push.ps1 -Tag 1 -Push -Services iam-service,catalogo-service
#>

param(
  [string]$Tag = "1.0.0",
    [switch]$Push,
    [string[]]$Services
)

# Paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path "$scriptDir\..").ProviderPath
$servicesPath = Join-Path $repoRoot 'services'

Write-Host "Repo root: $repoRoot"
Write-Host "Services path: $servicesPath"

# Discover service directories if not provided
if (-not $Services -or $Services.Count -eq 0) {
    $serviceDirs = Get-ChildItem -Path $servicesPath -Directory | Where-Object { $_.Name -like '*-service' } | Select-Object -ExpandProperty Name
} else {
    $serviceDirs = $Services
}

if (-not $serviceDirs -or $serviceDirs.Count -eq 0) {
    Write-Error "No service directories found under $servicesPath."
    exit 1
}

# Mapping for canonical image names (adjust here if you want different names)
function Get-ImageName($svcName) {
    switch ($svcName) {
        'iam-service' { return 'emeday17/iam-service' }
        'catalogo-service' { return 'emeday17/eventos-catalogo' }
        'proveedores-service' { return 'emeday17/eventos-proveedores' }
        'contratacion-service' { return 'emeday17/eventos-contratacion' }
        default { return "emeday17/$svcName" }
    }
}

foreach ($svc in $serviceDirs) {
    $dockerfile = Join-Path -Path $servicesPath -ChildPath "$svc\Dockerfile"
    if (-not (Test-Path $dockerfile)) {
      Write-Warning "Skipping $($svc): Dockerfile not found at $dockerfile"
        continue
    }

    $imageName = Get-ImageName $svc
    $fullTag = "$($imageName):$Tag"

    Write-Host "\nBuilding $fullTag from $dockerfile (context: $repoRoot)" -ForegroundColor Cyan

    # Build with repo root as context so shared libs are available
    $buildCmd = "docker build -t $fullTag -f `"$dockerfile`" `"$repoRoot`""
    Write-Host "Running: $buildCmd"
    iex $buildCmd

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed for $svc (exit $LASTEXITCODE). Aborting."
        exit $LASTEXITCODE
    }

    if ($Push) {
        Write-Host "Pushing $fullTag" -ForegroundColor Green
        $pushCmd = "docker push $fullTag"
        iex $pushCmd
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Push failed for $svc (exit $LASTEXITCODE). Aborting."
            exit $LASTEXITCODE
        }
    }
}

Write-Host "\nAll done." -ForegroundColor Green

# Helpful reminder
if ($Push) {
    Write-Host "Reminder: Ensure you are logged in to DockerHub (docker login) and have permissions to push to emeday17/* images." -ForegroundColor Yellow
}

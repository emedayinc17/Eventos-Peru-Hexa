<#
.SYNOPSIS
  Build and optionally push the frontend Docker image for the project.

.DESCRIPTION
  Builds the frontend Docker image using the repository root as build context (so shared libs are available),
  tags the image as `emeday17/eventos-frontend:<Tag>` and optionally pushes it to DockerHub.

.PARAMETER Tag
  The image tag to apply to the built image. Default: "1.0.0-prod".

.PARAMETER Push
  If present, the script will `docker push` the image after a successful build.

.PARAMETER ApiBase
  Optional build-arg value for `VITE_API_BASE_URL` that will be embedded at build time (default: "/api").

.EXAMPLE
  .\build-and-push-frontend.ps1 -Tag 1.0.0 -Push -ApiBase "/api"
#>

param(
  [string]$Tag = "1.0.0",
  [switch]$Push,
  [string]$ApiBase = "/api"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path "$scriptDir").ProviderPath
$frontendDir = Join-Path $repoRoot 'frontend'
$dockerfile = Join-Path $frontendDir 'Dockerfile'

if (-not (Test-Path $dockerfile)) {
  Write-Error "Dockerfile not found at $dockerfile"
  exit 1
}

$imageName = 'emeday17/eventos-frontend'
$fullTag = "$($imageName):$Tag"

Write-Host "Building frontend image: $fullTag" -ForegroundColor Cyan
Write-Host "Frontend Dockerfile: $dockerfile (context: $repoRoot)"
Write-Host "Using VITE_API_BASE_URL=$ApiBase"

$buildCmd = "docker build -t $fullTag -f `"$dockerfile`" --build-arg VITE_API_BASE_URL=`"$ApiBase`" `"$repoRoot`""
Write-Host "Running: $buildCmd"

iex $buildCmd
if ($LASTEXITCODE -ne 0) {
  Write-Error "Build failed for frontend (exit $LASTEXITCODE). Aborting."
  exit $LASTEXITCODE
}

if ($Push) {
  Write-Host "Pushing $fullTag" -ForegroundColor Green
  $pushCmd = "docker push $fullTag"
  iex $pushCmd
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Push failed for frontend (exit $LASTEXITCODE). Aborting."
    exit $LASTEXITCODE
  }
}

Write-Host "Frontend image build completed: $fullTag" -ForegroundColor Green
if ($Push) { Write-Host "Image pushed." -ForegroundColor Green }

Write-Host "Reminder: ensure you are logged in to DockerHub (docker login) and have permission to push to emeday17/* images." -ForegroundColor Yellow

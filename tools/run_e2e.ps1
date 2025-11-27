<#
Run E2E authenticated tests locally.

Usage (PowerShell):
  Set any env vars you need, then:
  $env:E2E_RUN = '1'; .\tools\run_e2e.ps1

Example setting service URLs and credentials:
  $env:IAM_URL = 'http://127.0.0.1:8010/iam'
  $env:CONTRATACION_URL = 'http://127.0.0.1:8040/contratacion'
  $env:TEST_CLIENT_EMAIL = 'demo@eventos.pe'
  $env:TEST_CLIENT_PASSWORD = 'Admin_2025!'
  $env:E2E_RUN = '1'
  python -m pytest tests/e2e -q
#>

if (-not $env:E2E_RUN) {
    Write-Host "E2E_RUN not set. Setting it to '1' for this run."
    $env:E2E_RUN = '1'
}

Write-Host "Running E2E tests (tests/e2e)..."
python -m pytest tests/e2e -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "E2E tests failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
Write-Host "E2E tests finished successfully."

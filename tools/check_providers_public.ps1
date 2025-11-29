param(
  [string]$Base = "http://localhost:5173/api",
  [int]$Sample = 5
)

$uri = "$Base/proveedores/v1/proveedores"
Write-Host "Checking public providers endpoint: $uri"

try {
  $resp = Invoke-RestMethod -Uri $uri -Method Get -ErrorAction Stop
} catch {
  Write-Host "ERROR: Request failed:`n$($_.Exception.Message)" -ForegroundColor Red
  exit 2
}

if ($null -eq $resp) {
  Write-Host "No data returned (null)" -ForegroundColor Yellow
  exit 1
}

# Normalize: if response is object with data/items, extract
if ($resp -is [System.Collections.IEnumerable] -and -not ($resp -is [string])) {
  $items = $resp
} elseif ($resp.data) {
  $items = $resp.data
} elseif ($resp.items) {
  $items = $resp.items
} else {
  $items = @($resp)
}

$count = ($items | Measure-Object).Count
Write-Host "OK. Providers returned: $count"

if ($count -eq 0) { exit 1 }

Write-Host "`nSample providers:`n"
$i = 0
foreach ($p in $items) {
  $i++
  $id = $p.id
  $name = $p.nombre_comercial -or $p.nombre -or $p.razon_social
  $rating = $p.rating_prom
  $email = $p.email
  $phone = $p.telefono
  $direccion = $p.direccion
  $contacto = $p.contacto
  Write-Host "$i. id=$id name=$name rating=$rating email=$email phone=$phone direccion=$direccion contacto=$contacto"
  if ($i -ge $Sample) { break }
}

exit 0

Param()
$repo = "E:\eventos-peru-hexagonal"  # ajusta si tu ruta es distinta
$env:PYTHONPATH = "$repo\libs\shared;$(Get-Location)"
uvicorn app.entrypoints.fastapi.main:app --host 0.0.0.0 --port 8030 --reload

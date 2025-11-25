$env:PYTHONPATH="E:\eventos-peru-hexagonal\libs\shared;E:\eventos-peru-hexagonal\services\contratacion-service"
cd E:\eventos-peru-hexagonal\services\contratacion-service
python -m uvicorn app.entrypoints.fastapi.main:app --host 0.0.0.0 --port 8040 > server.log 2>&1
@echo off
REM API Gateway runner
REM Inicia el gateway en puerto 8000

set GATEWAY_DIR=%~dp0
cd /d "%GATEWAY_DIR%"

echo.
echo ================================================
echo   Starting API Gateway on http://localhost:8000
echo ================================================
echo.
echo Routing:
echo   /api/iam/*          -^> localhost:8010
echo   /api/catalogo/*     -^> localhost:8020
echo   /api/proveedores/*  -^> localhost:8030
echo   /api/contratacion/* -^> localhost:8040
echo.
echo ================================================
echo.

REM Activar venv del proyecto root
call "%GATEWAY_DIR%..\Scripts\activate.bat"

REM Instalar httpx si no está
python -c "import httpx" 2>nul || pip install httpx

REM Correr gateway
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause

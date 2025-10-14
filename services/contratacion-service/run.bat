:: run.bat standardized
@echo off
setlocal enabledelayedexpansion
set "HERE=%~dp0"
for %%I in ("%HERE%..\..") do set "REPO=%%~fI"

if not defined PYTHONPATH set "PYTHONPATH=%REPO%\libs\shared;%HERE%"

if not exist "%HERE%\.env" (
  if exist "%HERE%\.env.example" copy "%HERE%\.env.example" "%HERE%\.env" >nul
)

if "%APP_HOST%"=="" set "APP_HOST=0.0.0.0"
if "%APP_PORT%"=="" set "APP_PORT=8040"

cd /d "%HERE%"
python -m uvicorn app.entrypoints.fastapi.main:app --host %APP_HOST% --port %APP_PORT% --env-file "%HERE%\.env"
endlocal

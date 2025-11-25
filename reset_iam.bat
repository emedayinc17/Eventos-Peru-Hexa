@echo off
echo Reseteando usuario app_iam (Nuclear Option)...
type db\force_reset_iam.sql | mysql -u root -p
if %errorlevel% neq 0 (
    echo Error al ejecutar el script SQL.
    pause
    exit /b %errorlevel%
)
echo Usuario app_iam reseteado correctamente.
pause

@echo off
echo Arreglando usuario app_iam...
type db\fix_iam_user.sql | mysql -u root -p
if %errorlevel% neq 0 (
    echo Error al ejecutar el script SQL.
    pause
    exit /b %errorlevel%
)
echo Usuario app_iam arreglado.
pause

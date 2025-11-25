@echo off
echo Poblando base de datos con datos masivos (script2.sql)...
echo Por favor ingresa tu contrasena de root de MySQL cuando se te pida.
type db\script2.sql | mysql -u root -p
if %errorlevel% neq 0 (
    echo Error al ejecutar el script SQL.
    pause
    exit /b %errorlevel%
)
echo Datos masivos cargados correctamente.
pause

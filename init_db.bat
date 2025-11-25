@echo off
echo Inicializando base de datos con bosstrap_remaste.sql...
echo Por favor ingresa tu contrasena de root de MySQL cuando se te pida.
type db\bosstrap_remaste.sql | mysql -u root -p
if %errorlevel% neq 0 (
    echo Error al ejecutar el script SQL. Asegurate de que mysql este en tu PATH.
    pause
    exit /b %errorlevel%
)
echo Base de datos inicializada correctamente.
pause

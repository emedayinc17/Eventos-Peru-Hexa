# Ejecutar tests - `proveedores-service`

Instrucciones rápidas para ejecutar la suite de pruebas canónica del servicio `proveedores-service`.

Requisitos
- Python (el proyecto usa `python3.12` en el entorno, pero Python 3.10+ funciona).
- Tener un entorno virtual activado (recomendado).
- `pytest` y `pytest-html` instalados en el entorno de ejecución.

Instalación de dependencias (PowerShell)
```powershell
# Desde la raíz del repositorio (Windows PowerShell)
& .\Scripts\Activate.ps1    # activa el virtualenv del repo (si existe)
python -m pip install --upgrade pip
pip install pytest pytest-html
```

Ejecutar los tests (recomendado desde la raíz del repo)
```powershell
# Ejecuta la suite canónica del servicio proveedores
pytest services\proveedores-service\tests
```

Notas importantes
- El archivo `pytest.ini` dentro de `services/proveedores-service` está configurado para:
  - Generar un informe HTML en `services/proveedores-service/tests/report.html`.
  - Limitar la colección de tests al archivo `test_full_flow.py` (archivo canónico con todas las pruebas).
- Si prefieres ejecutar únicamente el archivo canónico:
```powershell
pytest services\proveedores-service\tests\test_full_flow.py -q
```

Salida / informe
- Después de la ejecución, abre el informe HTML en tu navegador:
  - `services/proveedores-service/tests/report.html`

Diagnóstico rápido
- Si pytest falla con un error de plugin (por ejemplo, `--html` desconocido), instala `pytest-html`:
```powershell
pip install pytest-html
```
- Si las pruebas intentan usar una base de datos real, el archivo `test_full_flow.py` contiene mocks/fakes y no necesita una DB. Asegúrate de ejecutar desde el entorno virtual donde instalaste `pytest`.

Contacto
- Si quieres que agregue comandos para generar un reporte con timestamp, o que haga que el `report.html` se publique en otro directorio, dime y lo ajusto.

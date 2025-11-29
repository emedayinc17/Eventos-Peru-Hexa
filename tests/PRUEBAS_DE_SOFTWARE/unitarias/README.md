# Unitarias

Descripción
-----------
Pruebas unitarias de lógica de dominio y utilidades que no dependen de
servicios externos. Deben ser rápidas y deterministas.

Prerequisitos
------------
- Python 3.8+ instalado
- Crear y activar un entorno virtual (recomendado)

Instalación de dependencias
---------------------------
Instalar las dependencias necesarias para ejecutar los tests Python:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell (Windows)
pip install -r tests/requirements.txt
```

Ejecución
---------
Ejecutar sólo los tests unitarios:

```bash
pytest tests/PRUEBAS_DE_SOFTWARE/unitarias -q
```

Consideraciones
---------------
- Algunos tests importan utilidades desde `tools/`. Si dichas funciones
	no están presentes, los tests se saltarán automáticamente.
- Mantener los tests pequeños y sin dependencias externas para facilitar
	ejecución en CI.

Buenas prácticas
----------------
- Preferir funciones puras y desacopladas.
- Usar fixtures para datos comunes.
- No tocar recursos externos (DB, APIs) en pruebas unitarias.
Pruebas unitarias para microservicios (IAM, Catálogo, Proveedores, Contratación).

Objetivo:
- Validar entidades y casos de uso aislados.
- No deben depender de MySQL: usar mocks (pytest + unittest.mock / pytest-mock).

Ejecutar:
```bash
pytest tests/PRUEBAS_DE_SOFTWARE/unitarias/
```

Buenas prácticas:
- Mantener tests pequeños y rápidos.
- Usar fixtures para datos comunes.

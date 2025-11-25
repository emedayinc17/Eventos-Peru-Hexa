Generar presentación PPT con resumen del servicio IAM

Este pequeño script crea un archivo `IAM_Service_Resumen.pptx` con 2 diapositivas que describen el servicio IAM.

Requisitos
- Python 3.x
- Paquete `python-pptx` (instalar si no está presente)

Instalación (Windows PowerShell):

```powershell
python -m pip install --user python-pptx
```

Generar la presentación:

```powershell
python .\tools\generate_iam_ppt.py
```

El script generará `IAM_Service_Resumen.pptx` en la raíz del repositorio. Si necesitas texto adicional, logos o formato personalizado, edita `tools/generate_iam_ppt.py`.

# Análisis de Vulnerabilidades

Descripción
-----------
Comandos y scripts para analizar imágenes Docker y código Python en busca
de vulnerabilidades y malas prácticas.

Herramientas y scripts incluidos
-------------------------------
- `bandit_run.sh` — ejecuta `bandit` recursivamente sobre el código y
  genera `bandit_report.txt` si `bandit` está instalado.
- `trivy_scan.sh` — escanea una imagen Docker; requiere pasar la imagen
  como argumento: `./trivy_scan.sh my-api-image:latest`.

Comandos de ejemplo
-------------------
Bandit (si lo instala):

```bash
./tests/PRUEBAS_DE_SEGURIDAD/analisis_vulnerabilidades/bandit_run.sh
```

Trivy (escaneo de imagen):

```bash
./tests/PRUEBAS_DE_SEGURIDAD/analisis_vulnerabilidades/trivy_scan.sh my-api-image:latest
```

Snyk (opcional, requiere cuenta):

```bash
snyk test --file=requirements.txt
```

Prerequisitos
------------
- `python` y `pip` para instalar `bandit` (`pip install bandit`).
- `trivy` para escanear imágenes (`brew install trivy` / paquete del SO).

Precauciones
-----------
- Ejecutar en entornos de análisis o CI. No ejecutar escaneos masivos en
  entornos de producción sin políticas.

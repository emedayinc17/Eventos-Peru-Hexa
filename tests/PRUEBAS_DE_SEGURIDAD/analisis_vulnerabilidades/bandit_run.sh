#!/usr/bin/env bash
echo "Ejecutando bandit contra el código Python..."

if ! command -v bandit >/dev/null 2>&1; then
	echo "bandit no está instalado. Instalar: pip install bandit"
	exit 0
fi

# Ejecuta un análisis recursivo y genera reporte en formato texto
bandit -r .. -lll -o bandit_report.txt
echo "Reporte generado: bandit_report.txt"

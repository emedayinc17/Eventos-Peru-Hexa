#!/usr/bin/env python3
"""Script para agregar servicios_adicionales al schema"""

# Leer el archivo
with open('services/contratacion-service/app/entrypoints/fastapi/schemas.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea donde está "notas: Optional[str] = None" y agregar después
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # Si encontramos la línea de notas en CrearPedidoDesdePaquete
    if 'notas: Optional[str] = None' in line and i > 10 and i < 30:
        # Agregar la nueva línea con la misma indentación
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f"{indent}servicios_adicionales: Optional[List['ItemCustom']] = None  # Servicios extras además del paquete\n")

# Escribir el archivo
with open('services/contratacion-service/app/entrypoints/fastapi/schemas.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Cambio aplicado correctamente en schemas.py")

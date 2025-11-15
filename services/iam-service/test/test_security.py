# test/test_security.py

import sys
from pathlib import Path

# Ruta completa de este archivo: .../services/iam-service/test/test_security.py
CURRENT = Path(__file__).resolve()

# Raíz del servicio IAM: .../services/iam-service  (aquí vive app/)
IAM_ROOT = CURRENT.parents[1]

# Raíz del proyecto: .../eventos-peru-hexagonal  (aquí debe vivir ev_shared/)
PROJECT_ROOT = CURRENT.parents[3]

for p in (IAM_ROOT, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.infrastructure.security.password_adapter import (
    hash_password,
    verify_password,
)


def test_verify_password_correcta():
    plain = "Admin123*"
    hashed = hash_password(plain)

    assert verify_password("Admin123*", hashed) is True


def test_verify_password_incorrecta():
    plain = "Admin123*"
    hashed = hash_password(plain)

    assert verify_password("Admin123", hashed) is False


#Prueba de caja blanca – Validación de funciones internas de seguridad
#Para el servicio IAM se implementaron pruebas unitarias orientadas a validar la lógica interna de manejo de contraseñas.
#Estas pruebas no interactúan con la API, sino directamente con los métodos internos del adaptador de seguridad (password_adapter), por lo que corresponden a pruebas de caja blanca.
#Las funciones hash_password() y verify_password() se prueban de manera aislada para confirmar:
#Que el sistema genera hashes seguros a partir de contraseñas en texto plano.
#Que el mecanismo de verificación reconoce correctamente contraseñas válidas.
#Que contraseñas incorrectas son rechazadas adecuadamente.
#El siguiente caso de prueba refleja este comportamiento:
#Contraseña correcta → verificación exitosa (True)
#Contraseña incorrecta → verificación fallida (False)
#Este tipo de pruebas asegura la confiabilidad del módulo de autenticación antes de integrarlo con los endpoints públicos (/auth/login) validados mediante pruebas de caja negra.
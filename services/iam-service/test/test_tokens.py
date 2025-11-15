# test/test_tokens.py

import sys
from pathlib import Path

# Ruta completa de este archivo: .../services/iam-service/test/test_tokens.py
CURRENT = Path(__file__).resolve()

# Raíz del servicio IAM: .../services/iam-service  (aquí vive app/)
IAM_ROOT = CURRENT.parents[1]

# Raíz del proyecto: .../eventos-peru-hexagonal  (aquí debe vivir ev_shared/)
PROJECT_ROOT = CURRENT.parents[3]

for p in (IAM_ROOT, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.infrastructure.security.jwt_adapter import (
    create_token,
    decode_token,
)


def test_create_token_payload_correcto():
    # Secret de prueba (solo para tests)
    secret = "CFJBN9D2O1S6TMKY43Z0VGI5E8RQXUHPL7AW"
    subject = "admin@test.com"
    claims = {"role": "ADMIN"}

    token = create_token(
        subject=subject,
        claims=claims,
        secret=secret,
        expires_minutes=15,
    )

    decoded = decode_token(token, secret=secret, algorithms=["HS256"])

    assert decoded["sub"] == subject
    assert decoded["role"] == "ADMIN"


#Prueba de caja blanca – Validación del módulo de generación y decodificación de JWT
#Esta prueba unitaria se enfocó en validar la lógica interna del adaptador de seguridad encargado de gestionar tokens JWT (jwt_adapter).
#Al tratarse de una función no expuesta como endpoint, y cuyo comportamiento depende del diseño interno del servicio IAM, corresponde a una prueba de caja blanca.
#El caso de prueba genera un token mediante la función create_token(), especificando un subject y un campo personalizado role. Posteriormente, el mismo token es decodificado con la función decode_token(), verificando que el payload contenga exactamente los valores esperados.
#Esta prueba asegura que:
#El token JWT se genere correctamente con los claims definidos.
#El campo estándar sub se incluya con el identificador del usuario.
#Los claims personalizados (p. ej., role) se incluyan de forma íntegra.
#La firma y estructura del token sean válidas.
#Con ello se valida la integridad del mecanismo de autenticación a nivel interno, independientemente del endpoint /auth/login, y se garantiza la correcta implementación del módulo de seguridad dentro de la arquitectura hexagonal.
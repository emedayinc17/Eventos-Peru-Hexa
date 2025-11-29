#!/usr/bin/env python3
"""Functional tests: Crear pedidos (3 casos).

Nota: Estos tests ejercitan endpoints HTTP; requieren servicios levantados.
"""
import requests
import json
from datetime import date, timedelta

# Configuración
API_BASE = "http://localhost:8000"
CLIENTE_EMAIL = "cliente@test.com"
CLIENTE_PASSWORD = "Cliente123!"

def login():
    response = requests.post(
        f"{API_BASE}/api/iam/login",
        json={"email": CLIENTE_EMAIL, "password": CLIENTE_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_crear_pedido_con_paquete(token):
    fecha_evento = (date.today() + timedelta(days=35)).isoformat()
    payload = {
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "fecha_evento": fecha_evento,
        "num_personas": 100,
        "hora_inicio": "18:00",
        "hora_fin": "23:00",
        "ubicacion": "Lima, Perú",
        "paquete_id": "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0",
        "notas": "Pedido de prueba con paquete"
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{API_BASE}/api/contratacion/pedidos", json=payload, headers=headers)
    assert res.status_code in (200, 201)

def test_crear_pedido_paquete_con_extras(token):
    fecha_evento = (date.today() + timedelta(days=40)).isoformat()
    payload = {
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "fecha_evento": fecha_evento,
        "num_personas": 100,
        "hora_inicio": "18:00",
        "hora_fin": "23:00",
        "ubicacion": "Lima, Perú",
        "paquete_id": "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0",
        "servicios_adicionales": [
            {"opcion_servicio_id": "88888888-8888-8888-8888-888888888888", "cantidad": 1}
        ],
        "notas": "Pedido con paquete + DJ adicional"
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{API_BASE}/api/contratacion/pedidos", json=payload, headers=headers)
    assert res.status_code in (200, 201)

def test_crear_pedido_custom(token):
    fecha_evento = (date.today() + timedelta(days=45)).isoformat()
    payload = {
        "tipo_evento_id": "22222222-2222-2222-2222-222222222222",
        "fecha_evento": fecha_evento,
        "num_personas": 50,
        "hora_inicio": "15:00",
        "hora_fin": "20:00",
        "ubicacion": "Lima, Perú",
        "items": [
            {"opcion_servicio_id": "77777777-7777-7777-7777-777777777777", "cantidad": 1},
            {"opcion_servicio_id": "88888888-8888-8888-8888-888888888888", "cantidad": 1}
        ]
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{API_BASE}/api/contratacion/pedidos", json=payload, headers=headers)
    assert res.status_code in (200, 201)

def test_flow_crear_pedidos():
    token = login()
    assert token is not None, "Necesita token de IAM para ejecutar pruebas funcionales"
    test_crear_pedido_con_paquete(token)
    test_crear_pedido_paquete_con_extras(token)
    test_crear_pedido_custom(token)

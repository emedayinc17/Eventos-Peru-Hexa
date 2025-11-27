# Catálogo Service

**Versión**: 1.0.0  
**Estado**: ✅ 100% Funcional  
**Puerto**: 8020  
**Base de Datos**: ev_catalogo, ev_paquetes

Este microservicio gestiona el catálogo completo de servicios de eventos, incluyendo tipos de eventos, servicios, opciones y paquetes predefinidos.

---

## 🎯 Responsabilidades

- ✅ Gestión de tipos de evento (bodas, cumpleaños, corporativos, etc.)
- ✅ Catálogo de servicios por tipo de evento
- ✅ Opciones de servicios con precios
- ✅ Paquetes predefinidos (combos)
- ✅ Consultas públicas del catálogo
- ✅ Administración del catálogo

---

## 🏗️ Arquitectura Hexagonal

```
catalogo-service/
├── app/
│   ├── domain/                 # Entidades y lógica de negocio
│   ├── application/            # Casos de uso
│   ├── infrastructure/         # Adaptadores (MySQL)
│   └── entrypoints/            # API REST (FastAPI)
│
└── test/                       # Tests
```

---

## 🔌 Endpoints

### Públicos

#### `GET /catalogo/health`
Health check.

#### `GET /catalogo/v1/tipos-evento`
Lista tipos de evento disponibles.

**Response**:
```json
{
  "total": 5,
  "tipos": [
    {
      "id": "uuid",
      "nombre": "Boda",
      "descripcion": "Eventos de matrimonio"
    }
  ]
}
```

#### `GET /catalogo/v1/servicios`
Lista servicios disponibles.

**Query Parameters**:
- `tipo_evento_id`: Filtrar por tipo de evento
- `skip`: Paginación (default: 0)
- `limit`: Límite (default: 50)

**Response**:
```json
{
  "total": 30,
  "servicios": [
    {
      "id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
      "nombre": "Fotografía Profesional",
      "tipo_evento_id": "uuid",
      "descripcion": "Servicio fotográfico completo"
    }
  ]
}
```

#### `GET /catalogo/v1/opciones-servicio`
Opciones de un servicio específico.

**Query Parameters**:
- `servicio_id`: ID del servicio (requerido)
- `fecha_evento`: Fecha para validar disponibilidad (opcional)

**Response**:
```json
{
  "total": 3,
  "opciones": [
    {
      "id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
      "servicio_id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
      "nombre": "Paquete Básico",
      "descripcion": "4 horas de cobertura",
      "precio_vigente": 1500.00,
      "moneda": "PEN"
    }
  ]
}
```

#### `GET /catalogo/v1/paquetes`
Lista paquetes predefinidos.

**Response**:
```json
{
  "total": 16,
  "paquetes": [
    {
      "id": "uuid",
      "codigo": "PKG-001",
      "nombre": "Paquete Bodas Premium",
      "descripcion": "Todo incluido",
      "precio_total": 8500.00,
      "num_items": 5
    }
  ]
}
```

#### `GET /catalogo/v1/paquetes/{id}`
Detalle completo de un paquete.

**Response**:
```json
{
  "id": "uuid",
  "nombre": "Paquete Bodas Premium",
  "items": [
    {
      "opcion_servicio_id": "uuid",
      "cantidad": 1,
      "precio_unitario": 1500.00
    }
  ],
  "precio_total": 8500.00
}
```

---

## 📊 Datos Disponibles

- **Tipos de Evento**: 5
- **Servicios**: 30
- **Opciones de Servicio**: 90+
- **Paquetes**: 16

---

## 🚀 Ejecución

```powershell
cd services/catalogo-service
.\run.bat
```

Servicio disponible en `http://localhost:8020`

---

**Última Actualización**: 27 de Noviembre, 2025
# Roadmap - Sistema Eventos Perú

**Estado Actual**: ✅ Sistema 100% funcional en desarrollo  
**Fecha**: 27 de Noviembre, 2025  
**Branch**: emeday

---

## ✅ Completado (v1.0.0)

### Backend
- ✅ **Arquitectura Hexagonal** implementada (4 servicios)
- ✅ **IAM Service**: Autenticación JWT, gestión de usuarios
- ✅ **Catálogo Service**: Tipos de evento, servicios, opciones, paquetes
- ✅ **Proveedores Service**: Gestión de proveedores, holds temporales, disponibilidad
- ✅ **Contratación Service**: Pedidos, items, estados, asignación de proveedores
- ✅ **Base de Datos**: MySQL 8.0 con 7 schemas independientes
- ✅ **Seguridad**: JWT HS256, bcrypt_sha256, roles ADMIN/CLIENTE
- ✅ **Comunicación Inter-Servicios**: HTTP interno con INTERNAL_SERVICE_TOKEN
- ✅ **Tests E2E**: 100% éxito (3 flujos, 27 endpoints validados)
- ✅ **Documentación**: API completa + reporte de tests

### Datos de Prueba
- ✅ 152 usuarios (CLIENTE/ADMIN)
- ✅ 30 servicios de eventos
- ✅ 50 proveedores con habilidades
- ✅ 16 paquetes predefinidos
- ✅ Scripts de limpieza y validación

---

## 🔄 En Progreso (v1.1.0)

### Frontend
- 🔄 Interfaz web (HTML/CSS/JS vanilla)
- 🔄 Autenticación con JWT
- 🔄 Dashboard cliente: crear pedidos, consultar estado
- 🔄 Dashboard admin: gestión de pedidos, asignación de proveedores
- 🔄 Catálogo público de servicios/paquetes

### Mejoras Backend
- 🔄 OpenAPI/Swagger para todos los servicios
- 🔄 Logs estructurados con correlation_id
- 🔄 Health checks mejorados (/health sin DB, /ready con DB)

---

## 📋 Próximos Pasos (v1.2.0)

### Observabilidad
- [ ] Implementar X-Correlation-ID en headers
- [ ] Logging centralizado (ELK Stack o similar)
- [ ] Métricas de performance (Prometheus/Grafana)
- [ ] Alertas automáticas

### Optimización
- [ ] Circuit breaker para llamadas HTTP internas
- [ ] Cachear catálogo de servicios (raramente cambia)
- [ ] Async calls entre servicios
- [ ] Pool de conexiones DB optimizado

### Testing
- [ ] Tests unitarios adicionales (coverage >80%)
- [ ] Tests de carga (JMeter/Locust)
- [ ] Tests de integración entre servicios
- [ ] Cleanup automático en teardown de tests

### Seguridad
- [ ] Implementar refresh tokens
- [ ] Rotación de secrets JWT
- [ ] Rate limiting por endpoint
- [ ] Validación de inputs más estricta

---

## 🚀 Futuro (v2.0.0)

### Contenedores y Orquestación
- [ ] Dockerfiles multi-stage optimizados
- [ ] Docker Compose para ambiente local
- [ ] Kubernetes manifests (Deployments, Services, Ingress)
- [ ] StatefulSet para MySQL en K8s
- [ ] ConfigMaps y Secrets en K8s
- [ ] Vault para manejo de credenciales

### Kubernetes
- [ ] Readiness/Liveness probes
- [ ] HorizontalPodAutoscaler (HPA)
- [ ] NetworkPolicies
- [ ] ResourceQuotas y LimitRanges
- [ ] Ingress con TLS (HTTPS)

### Workers y Jobs
- [ ] Cronjob K8s para limpiar holds expirados
- [ ] Worker de envío de emails (outbox pattern)
- [ ] Worker de notificaciones push
- [ ] Procesamiento asíncrono de tareas pesadas

### Nuevas Funcionalidades
- [ ] Sistema de notificaciones (email, SMS, push)
- [ ] Pagos en línea (pasarela de pago)
- [ ] Confirmación automática de reservas
- [ ] Dashboard de analytics para admin
- [ ] Sistema de calificaciones de proveedores
- [ ] Chat en tiempo real (cliente ↔ proveedor)

### Mensajería
- [ ] Implementar servicio de mensajería completo
- [ ] Outbox pattern para eventos
- [ ] Message broker (RabbitMQ/Kafka)
- [ ] Event sourcing para auditoria

---

## 🔧 Deuda Técnica

### Alta Prioridad
- [ ] Implementar validación JWT en endpoints admin de Catálogo
- [ ] Estandarizar nombres de campos (precio_vigente vs monto)
- [ ] Completar tests de endpoints admin no críticos
- [ ] Documentación de arquitectura (diagramas de secuencia)

### Media Prioridad
- [ ] Refactorizar serialización de decimales
- [ ] Normalizar formato de responses (pagination)
- [ ] Migrar de HS256 a RS256 (JWT con clave pública)
- [ ] Implementar versionado de API (v1, v2)

### Baja Prioridad
- [ ] Soporte para múltiples idiomas (i18n)
- [ ] Modo offline (PWA)
- [ ] Migración a Python 3.13

---

## 📚 Documentación Pendiente

- [ ] Diagramas de arquitectura (C4 Model)
- [ ] Diagramas de secuencia para flujos complejos
- [ ] Guía de contribución
- [ ] Manual de despliegue
- [ ] Troubleshooting guide
- [ ] API versioning strategy

---

## ⚠️ Consideraciones de Producción

**Antes de desplegar a producción**:

1. **Seguridad**:
   - Cambiar `INTERNAL_SERVICE_TOKEN` de "dev-internal-token-change-in-production"
   - Rotar `SECRET_KEY` de JWT
   - Habilitar HTTPS obligatorio
   - Configurar CORS restrictivo (solo dominios autorizados)
   - Implementar rate limiting

2. **Base de Datos**:
   - Backups automáticos
   - Replicación master-slave
   - Índices optimizados
   - Monitoreo de queries lentas

3. **Infraestructura**:
   - Load balancer
   - Auto-scaling
   - Health checks configurados
   - Disaster recovery plan

4. **Monitoreo**:
   - APM (Application Performance Monitoring)
   - Error tracking (Sentry)
   - Uptime monitoring
   - Alertas 24/7

---

**Última Actualización**: 27 de Noviembre, 2025  
**Próxima Revisión**: Al completar Frontend v1.0

# 🧪 Checklist de Testing Manual - Frontend

**Fecha:** 27 de Noviembre, 2025  
**URL Local:** http://localhost:5174  
**Backend API:** http://localhost:8000

---

## ✅ Pre-requisitos

- [ ] Servidor backend corriendo (FastAPI en puerto 8000)
- [ ] Base de datos PostgreSQL activa y con datos de prueba
- [ ] Frontend corriendo (Vite en puerto 5174)
- [ ] Navegador con DevTools abierto para revisar errores

---

## 📋 1. Vistas Públicas (Sin Autenticación)

### 1.1 Home (`/`)
- [ ] La página carga correctamente
- [ ] Se muestra el hero section con título y descripción
- [ ] Botones de CTA funcionan (navegan a /paquetes y /login)
- [ ] Sección de features se muestra correctamente
- [ ] Footer se muestra con información de contacto
- [ ] Navbar muestra botones "Iniciar Sesión" y "Registrarse"

### 1.2 Login (`/login`)
- [ ] Formulario de login se muestra correctamente
- [ ] Tab de "Registro" funciona y cambia el formulario
- [ ] **Login con credenciales correctas:**
  - Email: admin@eventos.com
  - Password: admin123
  - [ ] Se muestra mensaje de éxito o redirección
  - [ ] Usuario es redirigido a /admin/dashboard
  - [ ] Token se guarda en localStorage
- [ ] **Login con credenciales incorrectas:**
  - [ ] Se muestra mensaje de error
  - [ ] No se redirige
- [ ] **Registro de nuevo usuario:**
  - [ ] Formulario tiene todos los campos (nombre, apellido, email, password, teléfono)
  - [ ] Validación de email funciona
  - [ ] Validación de password mínimo 6 caracteres
  - [ ] Al registrar exitosamente, muestra mensaje y sugiere login

### 1.3 Paquetes Públicos (`/paquetes`)
- [ ] Grid de paquetes se carga correctamente
- [ ] Filtro por "Tipo de Evento" funciona
- [ ] Buscador filtra por nombre/descripción
- [ ] Contador de paquetes encontrados es correcto
- [ ] Cada card muestra: nombre, descripción, tipo, servicios incluidos, precio
- [ ] Botón "Ver Detalle" navega a `/paquetes/:id`
- [ ] CTA "Iniciar Sesión" y "Crear Cuenta" funcionan
- [ ] Empty state se muestra si no hay paquetes

### 1.4 Detalle de Paquete (`/paquetes/:id`)
- [ ] Se muestra información completa del paquete
- [ ] Breadcrumb funciona (link a /paquetes)
- [ ] Lista de servicios incluidos se muestra con precios
- [ ] Cálculo de ahorro es correcto (suma servicios - precio paquete)
- [ ] Sidebar muestra precio, estadísticas
- [ ] **Si NO está autenticado:**
  - [ ] Botón "Iniciar Sesión para Continuar" redirige a /login con redirect
  - [ ] Botón "Crear Cuenta" redirige a /login?register=true
- [ ] **Si está autenticado:**
  - [ ] Botón "Seleccionar Paquete" redirige a /cliente/pedido/nuevo con query params

### 1.5 Proveedores (`/proveedores`)
- [ ] Grid de proveedores se carga (o muestra empty state si no hay datos)
- [ ] Buscador filtra por nombre/razón social/RUC
- [ ] Cada card muestra: avatar con iniciales, nombre comercial, razón social, email, teléfono, estado
- [ ] Badge de estado (Activo/Inactivo) con colores correctos
- [ ] CTA "Registrarse como Proveedor" funciona

---

## 🧑‍💼 2. Vistas de Cliente (Requiere autenticación como CLIENTE)

**Usuario de prueba:**
- Email: cliente@test.com
- Password: cliente123

### 2.1 Dashboard Cliente (`/cliente/dashboard`)
- [ ] Tarjetas de estadísticas muestran:
  - [ ] Total de pedidos
  - [ ] Pedidos pendientes
  - [ ] Pedidos confirmados
  - [ ] Próximos eventos
- [ ] Lista de pedidos recientes se muestra
- [ ] Botones de acción rápida funcionan:
  - [ ] "Crear Nuevo Pedido" → /cliente/pedido/nuevo
  - [ ] "Ver Mis Pedidos" → /cliente/mis-pedidos
  - [ ] "Explorar Paquetes" → /cliente/paquetes

### 2.2 Paquetes Cliente (`/cliente/paquetes`)
- [ ] Grid de paquetes similar a vista pública
- [ ] Filtro por tipo de evento funciona
- [ ] Botón "Seleccionar" redirige a wizard con query params correctos
- [ ] Cada paquete muestra servicios incluidos (primeros 3 + contador)

### 2.3 Crear Pedido - Wizard (`/cliente/pedido/nuevo`) **CRÍTICO**

#### **Paso 1: Tipo y Paquete**
- [ ] Dropdown de "Tipo de Evento" se carga con opciones
- [ ] Al seleccionar tipo, se filtran paquetes disponibles
- [ ] Paquetes se muestran como radio buttons con descripción y precio
- [ ] Campo "Fecha del Evento":
  - [ ] Input de tipo date
  - [ ] Fecha mínima es +30 días desde hoy
  - [ ] No permite fechas pasadas
- [ ] Campo "Número de Invitados":
  - [ ] Input tipo number
  - [ ] Mínimo 10, máximo 1000
- [ ] Botón "Siguiente" deshabilitado hasta completar campos requeridos
- [ ] Indicador de progreso muestra paso 1/3

#### **Paso 2: Servicios Adicionales**
- [ ] Se muestran servicios disponibles (excluyendo los del paquete)
- [ ] Servicios agrupados por categoría
- [ ] Checkboxes funcionan correctamente
- [ ] Campo "Comentarios" permite texto (máx 500 caracteres)
- [ ] **Resumen de precios en tiempo real:**
  - [ ] Precio base del paquete
  - [ ] Suma de servicios adicionales seleccionados
  - [ ] Total calculado correctamente
- [ ] Botón "Anterior" regresa a paso 1 sin perder datos
- [ ] Botón "Siguiente" va a paso 3
- [ ] Indicador muestra paso 2/3

#### **Paso 3: Confirmación**
- [ ] Se muestra resumen completo:
  - [ ] Tipo de evento
  - [ ] Paquete seleccionado
  - [ ] Fecha del evento
  - [ ] Número de invitados
  - [ ] Servicios adicionales
  - [ ] Comentarios
  - [ ] **Total a pagar**
- [ ] Botón "Anterior" regresa a paso 2
- [ ] Botón "Confirmar Pedido":
  - [ ] Muestra loading state
  - [ ] Al éxito, muestra modal de confirmación
  - [ ] Modal tiene opciones: "Ver Mis Pedidos" y "Crear Otro Pedido"
- [ ] Indicador muestra paso 3/3

#### **Funcionalidad de Draft (Estado Borrador)**
- [ ] Al cambiar de paso, los datos se guardan en el store (draft)
- [ ] Si refresco la página en medio del wizard, los datos persisten
- [ ] Al confirmar, el draft se limpia

### 2.4 Mis Pedidos (`/cliente/mis-pedidos`)
- [ ] Se cargan solo los pedidos del usuario autenticado
- [ ] Filtro por "Estado" funciona (PENDIENTE, CONFIRMADO, etc.)
- [ ] Cada card muestra:
  - [ ] Icono de tipo de evento (💒 Boda, 👗 Quinceañera, etc.)
  - [ ] Tipo de evento, fecha, invitados
  - [ ] Badge de estado con color correcto
  - [ ] Total del pedido
  - [ ] Fecha de creación formateada
- [ ] Botón "Ver Detalles" abre modal con información completa
- [ ] **Modal de detalles muestra:**
  - [ ] Todos los datos del pedido
  - [ ] Paquete seleccionado
  - [ ] Servicios adicionales
  - [ ] Comentarios
- [ ] Botón "Cancelar" solo visible para pedidos PENDIENTE
- [ ] Al cancelar, pide confirmación y actualiza estado
- [ ] Empty state se muestra si no hay pedidos

### 2.5 Perfil (`/perfil`)
- [ ] Formulario se carga con datos actuales del usuario
- [ ] Avatar con iniciales se muestra correctamente
- [ ] Información se muestra: nombre completo, email, role
- [ ] **Formulario de Información Personal:**
  - [ ] Campos editables: nombre, apellido, teléfono
  - [ ] Email es readonly (con explicación)
  - [ ] Botón "Cancelar" resetea los cambios
  - [ ] Botón "Guardar Cambios" solo habilitado si hay cambios
  - [ ] Al guardar, muestra modal de éxito
  - [ ] Datos se actualizan en el store y localStorage
- [ ] **Formulario de Cambio de Contraseña:**
  - [ ] Campos: contraseña actual, nueva, confirmar nueva
  - [ ] Validación de mínimo 6 caracteres
  - [ ] Validación de coincidencia de contraseñas
  - [ ] Mensaje de error si no coinciden
  - [ ] Botón deshabilitado si hay errores
  - [ ] (NOTA: funcionalidad pendiente en backend)

---

## 👨‍💼 3. Vistas de Admin (Requiere autenticación como ADMIN)

**Usuario de prueba:**
- Email: admin@eventos.com
- Password: admin123

### 3.1 Dashboard Admin (`/admin/dashboard`)
- [ ] Estadísticas generales:
  - [ ] Total usuarios
  - [ ] Total pedidos
  - [ ] Pedidos pendientes
  - [ ] Ingresos totales
- [ ] Gráficos o tablas de actividad reciente
- [ ] Accesos rápidos a secciones principales

### 3.2 Tipos de Evento (`/admin/tipos-evento`)
- [ ] Tabla muestra todos los tipos de evento
- [ ] Columnas: Nombre, Descripción, Acciones
- [ ] SearchBar filtra por nombre/descripción
- [ ] **Botón "Nuevo Tipo":**
  - [ ] Abre modal con formulario
  - [ ] Campos: nombre (requerido), descripción (requerido)
  - [ ] Al guardar, cierra modal y actualiza tabla
- [ ] **Botón "Editar" (lápiz):**
  - [ ] Abre modal con datos precargados
  - [ ] Al guardar, actualiza fila en tabla
- [ ] **Botón "Eliminar" (basura):**
  - [ ] Muestra confirmación con nombre del tipo
  - [ ] Al confirmar, elimina y actualiza tabla
  - [ ] Maneja error si hay dependencias (paquetes usando ese tipo)

### 3.3 Servicios (`/admin/servicios`)
- [ ] Tabla muestra todos los servicios
- [ ] Columnas: Nombre, Categoría, Tipo Evento, Precio, Estado, Acciones
- [ ] SearchBar filtra correctamente
- [ ] **Crear/Editar Servicio:**
  - [ ] Nombre (text, required)
  - [ ] Descripción (textarea, required)
  - [ ] Categoría (select con 7 opciones: FOTOGRAFIA, VIDEO, CATERING, etc.)
  - [ ] Tipo Evento (select cargado dinámicamente)
  - [ ] Precio Unitario (number, min=0, step=0.01)
  - [ ] Disponible (checkbox)
  - [ ] Validaciones funcionan
  - [ ] Al guardar, actualiza tabla
- [ ] **Eliminar:** confirmación + actualización

### 3.4 Paquetes (`/admin/paquetes`)
- [ ] Tabla muestra todos los paquetes
- [ ] Columnas: Paquete, Tipo Evento, Servicios Incluidos (badges), Precio Base, Acciones
- [ ] Filtros: SearchBar + tipo de evento
- [ ] **Crear/Editar Paquete (Complejo):**
  - [ ] Nombre (required)
  - [ ] Descripción (required)
  - [ ] Tipo Evento (select, required)
  - [ ] Precio Base (number, required)
  - [ ] **Multi-select Servicios:**
    - [ ] Se muestran checkboxes en scrollable div
    - [ ] Servicios filtrados por tipo_evento_id seleccionado
    - [ ] Al cambiar tipo, se limpia selección de servicios
    - [ ] Cada checkbox muestra: nombre, categoría, precio
    - [ ] Contador de servicios seleccionados
    - [ ] Botón submit deshabilitado si no hay servicios
  - [ ] Al guardar, actualiza tabla con badges de servicios
- [ ] Eliminar funciona

### 3.5 Usuarios (`/admin/usuarios`)
- [ ] Tabla muestra todos los usuarios
- [ ] Columnas: Usuario (avatar+nombre), Email, Teléfono, Role, Estado, Acciones
- [ ] **Filtros:**
  - [ ] SearchBar (nombre/apellido/email)
  - [ ] Role (TODOS/CLIENTE/ADMIN)
  - [ ] Estado (TODOS/ACTIVO/INACTIVO)
- [ ] Avatar muestra iniciales (primera letra nombre + apellido)
- [ ] **Crear Usuario:**
  - [ ] Campos: nombre, apellido, email, teléfono, password, role, activo
  - [ ] Password requerido en creación
  - [ ] Email debe ser único
  - [ ] Role dropdown (CLIENTE/ADMIN)
  - [ ] Activo checkbox (default true)
- [ ] **Editar Usuario:**
  - [ ] Email readonly (con mensaje explicativo)
  - [ ] Password NO requerido (opcional para cambiar)
  - [ ] Otros campos editables
- [ ] **Eliminar:**
  - [ ] NO permite eliminar el propio usuario (check con authStore.user.id)
  - [ ] Muestra mensaje si intenta eliminarse a sí mismo
  - [ ] Confirmación con nombre del usuario

### 3.6 Pedidos (`/admin/pedidos`)
- [ ] Tabla muestra TODOS los pedidos del sistema
- [ ] Columnas: ID, Cliente, Tipo Evento, Fecha Evento, Invitados, Estado, Total, Acciones
- [ ] **Filtros:**
  - [ ] SearchBar (ID/usuario)
  - [ ] Estado dropdown
- [ ] Muestra usuario_nombre si está disponible, sino "Usuario #X"
- [ ] **Estado editable inline:**
  - [ ] Dropdown en la columna Estado
  - [ ] Al cambiar, trigger PUT request inmediatamente
  - [ ] Muestra loading durante actualización
  - [ ] Si falla, revierte el cambio y muestra error
- [ ] **Botón "Ver":**
  - [ ] Abre modal con detalles completos del pedido
  - [ ] Similar a vista de cliente
- [ ] **Botón "Eliminar":**
  - [ ] Confirmación
  - [ ] Elimina y actualiza tabla

---

## 🔒 4. Pruebas de Autenticación y Guards

### 4.1 Guards de Rutas
- [ ] Intentar acceder a `/cliente/dashboard` sin login → redirige a /login
- [ ] Intentar acceder a `/admin/dashboard` sin login → redirige a /login
- [ ] Intentar acceder a `/admin/*` como CLIENTE → redirige a /cliente/dashboard
- [ ] Intentar acceder a `/cliente/*` como ADMIN → permitido (admin puede ver vistas de cliente)
- [ ] Al hacer logout, token se elimina de localStorage
- [ ] Al hacer logout, usuario es redirigido a /

### 4.2 Persistencia de Sesión
- [ ] Iniciar sesión
- [ ] Refrescar página (F5)
- [ ] Usuario sigue autenticado
- [ ] Navbar/sidebar muestra información correcta
- [ ] Cerrar y reabrir navegador → sesión persiste

### 4.3 Interceptores de Axios
- [ ] Todas las requests incluyen header `Authorization: Bearer <token>`
- [ ] Si token expira (401), usuario es redirigido a /login
- [ ] Mensajes de error del backend se muestran correctamente

---

## 🎨 5. Pruebas de UI/UX

### 5.1 Responsiveness
- [ ] **Desktop (1920x1080):**
  - [ ] Layouts se ven correctos
  - [ ] Sidebar no colapsa
  - [ ] Grids muestran 3 columnas
- [ ] **Tablet (768px):**
  - [ ] Grids muestran 2 columnas
  - [ ] Sidebar se oculta y muestra burger menu
- [ ] **Mobile (375px):**
  - [ ] Grids muestran 1 columna
  - [ ] Navbar responsive
  - [ ] Forms se adaptan

### 5.2 Estados de Loading
- [ ] Spinners se muestran durante carga de datos
- [ ] Botones muestran estado "loading" durante submit
- [ ] No se puede hacer doble click en botones de submit

### 5.3 Estados Vacíos (Empty States)
- [ ] Se muestran cuando no hay datos
- [ ] Tienen iconos, título, mensaje
- [ ] Incluyen CTA cuando es apropiado

### 5.4 Validación de Formularios
- [ ] Campos requeridos muestran error si están vacíos
- [ ] Validación de email funciona
- [ ] Validación de números (min/max) funciona
- [ ] Mensajes de error son claros

### 5.5 Temas y Colores
- [ ] Primary color (red) se aplica correctamente
- [ ] Secondary color (slate) se usa en textos secundarios
- [ ] Badges de estado tienen colores correctos:
  - [ ] PENDIENTE: amarillo
  - [ ] CONFIRMADO: verde
  - [ ] EN_PROGRESO: azul
  - [ ] COMPLETADO: púrpura
  - [ ] CANCELADO: rojo

---

## 🐛 6. Pruebas de Errores

### 6.1 Manejo de Errores del Backend
- [ ] Error 404 (recurso no encontrado) → mensaje claro
- [ ] Error 400 (validación) → muestra detalles del error
- [ ] Error 401 (no autorizado) → redirige a login
- [ ] Error 403 (prohibido) → mensaje de acceso denegado
- [ ] Error 500 (server error) → mensaje genérico

### 6.2 Errores de Red
- [ ] Detener backend → muestra error de conexión
- [ ] Request timeout → muestra mensaje apropiado

### 6.3 Validaciones de Negocio
- [ ] Intentar crear pedido con fecha pasada → rechazado
- [ ] Intentar seleccionar paquete sin tipo → deshabilitado
- [ ] Intentar eliminar tipo de evento con paquetes asociados → error del backend manejado

---

## 📊 7. Pruebas de Datos

### 7.1 CRUD Completo
Para cada entidad (TiposEvento, Servicios, Paquetes, Usuarios, Pedidos):
- [ ] **Create:** Crear nuevo registro exitosamente
- [ ] **Read:** Listar todos los registros
- [ ] **Update:** Editar registro existente
- [ ] **Delete:** Eliminar registro

### 7.2 Filtros y Búsquedas
- [ ] Filtros combinados funcionan
- [ ] Búsqueda parcial funciona (case-insensitive)
- [ ] Contador de resultados es correcto

### 7.3 Paginación (si implementada)
- [ ] Botones de navegación funcionan
- [ ] Contador de páginas correcto
- [ ] Items por página configurable

---

## 🚀 8. Pruebas de Performance

- [ ] Tiempo de carga inicial < 3 segundos
- [ ] Navegación entre páginas es instantánea (lazy loading)
- [ ] Imágenes optimizadas
- [ ] No hay memory leaks (revisar en DevTools)
- [ ] Cache de Pinia funciona (no re-fetch si datos frescos < 5min)

---

## ✅ Checklist de Aprobación Final

- [ ] Todas las vistas públicas funcionan
- [ ] Todas las vistas de cliente funcionan
- [ ] Todas las vistas de admin funcionan
- [ ] CreateOrderWizard (CRÍTICO) funciona end-to-end
- [ ] Autenticación y guards funcionan
- [ ] Todas las operaciones CRUD funcionan
- [ ] No hay errores en consola del navegador
- [ ] No hay errores de TypeScript
- [ ] Responsive en móvil, tablet, desktop
- [ ] Manejo de errores es apropiado
- [ ] Performance aceptable

---

## 📝 Notas de Testing

**Problemas Encontrados:**

1. 

2. 

3. 

**Mejoras Sugeridas:**

1. 

2. 

3. 

---

**Tester:** _____________________  
**Fecha:** _____________________  
**Firma:** _____________________

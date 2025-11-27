// === RENDER CATALOGO ===
async function renderCatalogo(container, role) {
    container.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>Catálogo de Paquetes</h3>
        ${role === 'ADMIN' ? '<button class="btn btn-primary btn-sm" onclick="openPaqueteModal()">+ Nuevo Paquete</button>' : ''}
    </div>
    
    <div class="card mb-4 border-0 shadow-sm">
        <div class="card-body">
            <div class="row align-items-center">
                <div class="col-md-4">
                    <label for="filter-tipo-evento" class="form-label small text-muted">Filtrar por Tipo de Evento</label>
                    <select class="form-select" id="filter-tipo-evento" onchange="filterCatalogo()">
                        <option value="">Todos los eventos</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <div id="catalogo-list" class="row g-4">
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Cargando catálogo...</p>
        </div>
    </div>`;

    try {
        const tipos = await CatalogoService.getTiposEvento();
        const filterSelect = document.getElementById('filter-tipo-evento');
        tipos.forEach(t => {
            const option = document.createElement('option');
            option.value = t.id;
            option.textContent = t.nombre;
            filterSelect.appendChild(option);
        });

        await loadPaquetes();
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error al cargar catálogo: ${error.message}</div>`;
    }
}

async function filterCatalogo() {
    await loadPaquetes();
}

async function loadPaquetes() {
    const listContainer = document.getElementById('catalogo-list');
    const typeId = document.getElementById('filter-tipo-evento').value;
    const role = SessionManager.getSession().user.role;

    listContainer.innerHTML = `
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Cargando paquetes...</p>
        </div>`;

    try {
        const paquetes = await CatalogoService.getPaquetes(typeId || null);
        renderPaquetesList(paquetes, role);
    } catch (error) {
        listContainer.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error al cargar paquetes: ${error.message}</div></div>`;
    }
}

function renderPaquetesList(paquetes, role) {
    const listContainer = document.getElementById('catalogo-list');

    if (paquetes.length === 0) {
        listContainer.innerHTML = '<div class="col-12"><div class="alert alert-info">No hay paquetes disponibles para este filtro.</div></div>';
        return;
    }

    let html = '';
    paquetes.forEach(p => {
        let buttons = '';
        if (role === 'ADMIN') {
            buttons = `
            <button class="btn btn-outline-secondary btn-sm me-2" onclick="openPaqueteModal('${p.id}')">Editar</button>
            <button class="btn btn-outline-danger btn-sm" onclick="deletePaquete('${p.id}')">Eliminar</button>
        `;
        } else {
            const safeNombre = p.nombre.replace(/'/g, "\\'");
            const safeTipoId = p.tipo_evento_id || '';
            const safeTipoNombre = p.tipo_evento_nombre || '';

            buttons = `
            <button class="btn btn-primary btn-sm px-3" onclick="contratarPaquete('${p.id}', '${safeNombre}', ${p.monto_total}, '${safeTipoId}', '${safeTipoNombre}')">Contratar</button>
        `;
        }

        const badge = p.tipo_evento_nombre
            ? `<span class="badge bg-info bg-opacity-10 text-info rounded-pill mb-2">${p.tipo_evento_nombre}</span>`
            : `<span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill mb-2">General</span>`;

        html += `
    <div class="col-md-6 col-xl-4">
        <div class="card h-100">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        ${badge}
                        <h5 class="card-title fw-bold mb-0">${p.nombre}</h5>
                    </div>
                </div>
                <p class="card-text text-muted small mb-4">${p.descripcion}</p>
                <div class="d-flex align-items-end justify-content-between mt-auto">
                    <div>
                        <small class="text-muted d-block">Precio Total</small>
                        <h4 class="text-primary fw-bold mb-0">S/ ${p.monto_total.toFixed(2)}</h4>
                    </div>
                    <div>
                        ${buttons}
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    });
    listContainer.innerHTML = html;
}

// === RENDER PEDIDOS (IMPROVED WITH CARDS) ===
async function renderPedidos(container, role) {
    const title = role === 'ADMIN' ? 'Gestión de Contratos' : 'Mis Pedidos';
    container.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>${title}</h3>
    </div>
    <div id="pedidos-list" class="row g-4">
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Cargando pedidos...</p>
        </div>
    </div>`;

    try {
        let pedidos;
        if (role === 'ADMIN') {
            pedidos = await ContratacionService.getAllPedidos();
        } else {
            pedidos = await ContratacionService.getMisPedidos();
        }

        console.log("Pedidos loaded:", pedidos);

        const listContainer = document.getElementById('pedidos-list');

        if (!pedidos || pedidos.length === 0) {
            listContainer.innerHTML = '<div class="col-12"><div class="alert alert-info">No hay pedidos registrados.</div></div>';
            return;
        }

        let html = '';
        pedidos.forEach(p => {
            const estado = p.estado || p.status || 1;
            const fecha = p.fecha_evento || p.created_at;
            const paqueteNombre = p.paquete_nombre || 'Pedido Personalizado';
            const ubicacion = p.ubicacion || 'No especificada';
            const numPersonas = p.num_personas || '-';

            let badgeClass = 'bg-warning text-dark';
            let estadoText = 'PENDIENTE';
            if (estado === 1 || estado === 'PENDIENTE') {
                badgeClass = 'bg-warning text-dark';
                estadoText = 'PENDIENTE';
            } else if (estado === 2 || estado === 'CONFIRMADO' || estado === 'PAGADO') {
                badgeClass = 'bg-success';
                estadoText = 'CONFIRMADO';
            } else if (estado === 5 || estado === 'CANCELADO') {
                badgeClass = 'bg-danger';
                estadoText = 'CANCELADO';
            }

            html += `
            <div class="col-md-6 col-xl-4">
                <div class="card h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="flex-grow-1">
                                <span class="badge ${badgeClass} bg-opacity-75 rounded-pill mb-2">${estadoText}</span>
                                <h5 class="card-title fw-bold mb-1">${paqueteNombre}</h5>
                                <small class="text-muted">#${p.id.substring(0, 8)}</small>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex align-items-center mb-2">
                                <span class="text-muted small me-2">📅</span>
                                <span class="small">${new Date(fecha).toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                            </div>
                            <div class="d-flex align-items-center mb-2">
                                <span class="text-muted small me-2">📍</span>
                                <span class="small text-truncate">${ubicacion}</span>
                            </div>
                            <div class="d-flex align-items-center">
                                <span class="text-muted small me-2">👥</span>
                                <span class="small">${numPersonas} invitados</span>
                            </div>
                        </div>

                        <div class="border-top pt-3 mt-auto">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <small class="text-muted d-block">Total</small>
                                    <h4 class="text-primary fw-bold mb-0">S/ ${p.monto_total.toFixed(2)}</h4>
                                </div>
                                <button class="btn btn-outline-primary btn-sm" onclick="verDetallePedido('${p.id}')">
                                    Ver Detalle
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        });

        listContainer.innerHTML = html;

    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error al cargar pedidos: ${error.message}</div>`;
    }
}

async function verDetallePedido(id) {
    try {
        const modal = new bootstrap.Modal(document.getElementById('detallePedidoModal'));
        const contentDiv = document.getElementById('detalle-pedido-content');

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">Cargando detalle...</p>
            </div>`;

        modal.show();

        const detalle = await ContratacionService.getDetallePedido(id);
        console.log("Detalle pedido:", detalle);

        const pedido = detalle.pedido || detalle;
        const items = detalle.items || [];

        const estado = pedido.estado || pedido.status || 1;
        let estadoText = 'PENDIENTE';
        let badgeClass = 'bg-warning text-dark';
        if (estado === 1 || estado === 'PENDIENTE') {
            estadoText = 'PENDIENTE';
            badgeClass = 'bg-warning text-dark';
        } else if (estado === 2 || estado === 'CONFIRMADO') {
            estadoText = 'CONFIRMADO';
            badgeClass = 'bg-success';
        } else if (estado === 5 || estado === 'CANCELADO') {
            estadoText = 'CANCELADO';
            badgeClass = 'bg-danger';
        }

        let itemsHtml = '';
        if (items && items.length > 0) {
            items.forEach(item => {
                itemsHtml += `
                <div class="border-bottom pb-3 mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="fw-bold mb-1">${item.servicio_nombre || 'Servicio'}</h6>
                            <p class="text-muted small mb-1">${item.opcion_nombre || ''}</p>
                            <small class="text-muted">Cantidad: ${item.cantidad}</small>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold">S/ ${(item.precio_unit * item.cantidad).toFixed(2)}</div>
                            <small class="text-muted">S/ ${item.precio_unit.toFixed(2)} c/u</small>
                        </div>
                    </div>
                </div>`;
            });
        } else {
            itemsHtml = '<p class="text-muted text-center py-3">No hay items disponibles</p>';
        }

        contentDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">ID Pedido</label>
                    <div class="fw-bold">#${pedido.id}</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">Estado</label>
                    <div><span class="badge ${badgeClass} bg-opacity-75 rounded-pill">${estadoText}</span></div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">Fecha del Evento</label>
                    <div class="fw-bold">${new Date(pedido.fecha_evento).toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">Hora de Inicio</label>
                    <div class="fw-bold">${pedido.hora_inicio || '-'}</div>
                </div>
                <div class="col-md-12 mb-3">
                    <label class="text-muted small">Ubicación</label>
                    <div class="fw-bold">${pedido.ubicacion || 'No especificada'}</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">Número de Invitados</label>
                    <div class="fw-bold">${pedido.num_personas || '-'}</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-muted small">Monto Total</label>
                    <div class="h4 text-primary fw-bold mb-0">S/ ${pedido.monto_total.toFixed(2)}</div>
                </div>
            </div>

            <hr class="my-4">

            <h6 class="fw-bold mb-3">Servicios Incluidos</h6>
            ${itemsHtml}
        `;

    } catch (error) {
        console.error("Error al cargar detalle:", error);
        const contentDiv = document.getElementById('detalle-pedido-content');
        contentDiv.innerHTML = `<div class="alert alert-danger">Error al cargar el detalle: ${error.message}</div>`;
    }
}

// === RENDER PROVEEDORES ===
async function renderProveedores(container, role) {
    container.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>Proveedores</h3>
        ${role === 'ADMIN' ? '<button class="btn btn-primary btn-sm" onclick="openProveedorModal()">+ Nuevo Proveedor</button>' : ''}
    </div>
    <div id="proveedores-list">
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Cargando proveedores...</p>
        </div>
    </div>
`;

    try {
        const proveedores = await ProveedoresService.getAll();
        const listContainer = document.getElementById('proveedores-list');

        if (proveedores.length === 0) {
            listContainer.innerHTML = '<div class="alert alert-info">No hay proveedores registrados.</div>';
            return;
        }

        let html = `
        <div class="card overflow-hidden">
            <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                    <thead class="bg-light">
                        <tr>
                            <th class="py-3 ps-4">Nombre</th>
                            <th class="py-3">Categoría</th>
                            <th class="py-3">Precio Base</th>
                            <th class="py-3">Contacto</th>
                            ${role === 'ADMIN' ? '<th class="py-3 pe-4 text-end">Acciones</th>' : ''}
                        </tr>
                    </thead>
                    <tbody>`;

        proveedores.forEach(p => {
            const actions = role === 'ADMIN' ? `
            <td class="pe-4 text-end">
                <button class="btn btn-sm btn-outline-secondary me-1" onclick="openProveedorModal('${p.id}')">Editar</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteProveedor('${p.id}')">Eliminar</button>
            </td>` : '';

            html += `
            <tr>
                <td class="ps-4 fw-medium">${p.nombre}</td>
                <td><span class="badge bg-info bg-opacity-10 text-info rounded-pill text-dark">${p.categoria}</span></td>
                <td class="fw-bold">S/ ${p.precio_base.toFixed(2)}</td>
                <td class="text-muted small">${p.contacto || '-'}</td>
                ${actions}
            </tr>`;
        });

        html += '</tbody></table></div></div>';
        listContainer.innerHTML = html;

    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error al cargar proveedores: ${error.message}</div>`;
    }
}

// === RENDER USUARIOS ===
async function renderUsuarios(container, role) {
    if (role !== 'ADMIN') {
        container.innerHTML = '<div class="alert alert-danger">Acceso denegado</div>';
        return;
    }
    container.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>Gestión de Usuarios</h3>
        <button class="btn btn-primary btn-sm" onclick="openUsuarioModal()">+ Nuevo Usuario</button>
    </div>
    <div id="usuarios-list">
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Cargando usuarios...</p>
        </div>
    </div>
`;

    try {
        const usuarios = await UsuariosService.getAll();
        const listContainer = document.getElementById('usuarios-list');

        if (usuarios.length === 0) {
            listContainer.innerHTML = '<div class="alert alert-info">No hay usuarios registrados.</div>';
            return;
        }

        let html = `
    <div class="card overflow-hidden">
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
                <thead class="bg-light">
                    <tr>
                        <th class="py-3 ps-4">Nombre</th>
                        <th class="py-3">Email</th>
                        <th class="py-3">Rol</th>
                        <th class="py-3">Estado</th>
                        <th class="py-3 pe-4 text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>`;

        usuarios.forEach(u => {
            const statusBadge = u.status === 1 ? '<span class="badge bg-success bg-opacity-75 rounded-pill">Activo</span>' : '<span class="badge bg-secondary rounded-pill">Inactivo</span>';
            html += `
        <tr>
            <td class="ps-4 fw-medium">${u.nombre || 'Sin nombre'}</td>
            <td>${u.email}</td>
            <td><span class="badge bg-primary bg-opacity-10 text-primary rounded-pill">${u.role}</span></td>
            <td>${statusBadge}</td>
            <td class="pe-4 text-end">
                <button class="btn btn-sm btn-outline-secondary me-1" onclick="openUsuarioModal('${u.id}')">Editar</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUsuario('${u.id}')">Eliminar</button>
            </td>
        </tr>`;
        });

        html += '</tbody></table></div></div>';
        listContainer.innerHTML = html;

    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error al cargar usuarios: ${error.message}</div>`;
    }
}

// === ACTIONS & MODALS ===

// Usuario Actions
let currentUsuarioId = null;

async function openUsuarioModal(id = null) {
    currentUsuarioId = id;
    const modalEl = document.getElementById('usuarioModal');
    const modal = new bootstrap.Modal(modalEl);
    const title = document.getElementById('usuarioModalLabel');

    document.getElementById('usuario-form').reset();

    if (id) {
        title.textContent = 'Editar Usuario';
        try {
            const user = await UsuariosService.getById(id);
            document.getElementById('usuario-nombre').value = user.nombre || '';
            document.getElementById('usuario-email').value = user.email;
            document.getElementById('usuario-rol').value = user.role;
        } catch (error) {
            alert('Error al cargar usuario: ' + error.message);
            return;
        }
    } else {
        title.textContent = 'Nuevo Usuario';
    }

    modal.show();
}

async function saveUsuario() {
    const nombre = document.getElementById('usuario-nombre').value;
    const email = document.getElementById('usuario-email').value;
    const password = document.getElementById('usuario-password').value;
    const role = document.getElementById('usuario-rol').value;

    const data = { nombre, email, role };
    if (password) data.password = password;

    try {
        if (currentUsuarioId) {
            await UsuariosService.update(currentUsuarioId, data);
        } else {
            if (!password) {
                alert('La contraseña es obligatoria para nuevos usuarios');
                return;
            }
            await UsuariosService.create(data);
        }

        const modalEl = document.getElementById('usuarioModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        loadView('usuarios');

    } catch (error) {
        alert('Error al guardar usuario: ' + error.message);
    }
}

async function deleteUsuario(id) {
    if (confirm('¿Estás seguro de eliminar este usuario?')) {
        try {
            await UsuariosService.delete(id);
            loadView('usuarios');
        } catch (error) {
            alert('Error al eliminar usuario: ' + error.message);
        }
    }
}

// Proveedor Actions
let currentProveedorId = null;

async function openProveedorModal(id = null) {
    currentProveedorId = id;
    const modalEl = document.getElementById('proveedorModal');
    const modal = new bootstrap.Modal(modalEl);
    const title = document.getElementById('proveedorModalLabel');

    document.getElementById('proveedor-form').reset();

    if (id) {
        title.textContent = 'Editar Proveedor';
        try {
            const prov = await ProveedoresService.getById(id);
            document.getElementById('proveedor-nombre').value = prov.nombre;
            document.getElementById('proveedor-categoria').value = prov.categoria;
            document.getElementById('proveedor-contacto').value = prov.contacto || '';
            document.getElementById('proveedor-precio').value = prov.precio_base;
        } catch (error) {
            alert('Error al cargar proveedor: ' + error.message);
            return;
        }
    } else {
        title.textContent = 'Nuevo Proveedor';
    }

    modal.show();
}

async function saveProveedor() {
    const nombre = document.getElementById('proveedor-nombre').value;
    const categoria = document.getElementById('proveedor-categoria').value;
    const contacto = document.getElementById('proveedor-contacto').value;
    const precio_base = parseFloat(document.getElementById('proveedor-precio').value);

    const data = { nombre, categoria, contacto, precio_base };

    try {
        if (currentProveedorId) {
            await ProveedoresService.update(currentProveedorId, data);
        } else {
            await ProveedoresService.create(data);
        }

        const modalEl = document.getElementById('proveedorModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        loadView('proveedores');

    } catch (error) {
        alert('Error al guardar proveedor: ' + error.message);
    }
}

async function deleteProveedor(id) {
    if (confirm('¿Estás seguro de eliminar este proveedor?')) {
        try {
            await ProveedoresService.delete(id);
            loadView('proveedores');
        } catch (error) {
            alert('Error al eliminar proveedor: ' + error.message);
        }
    }
}

// Paquete Actions
let currentPaqueteId = null;

async function openPaqueteModal(id = null) {
    currentPaqueteId = id;
    const modalEl = document.getElementById('paqueteModal');
    const modal = new bootstrap.Modal(modalEl);
    const title = document.getElementById('paqueteModalLabel');

    document.getElementById('paquete-form').reset();

    if (id) {
        title.textContent = 'Editar Paquete';
        try {
            const paquete = await CatalogoService.getById(id);
            document.getElementById('paquete-nombre').value = paquete.nombre;
            document.getElementById('paquete-descripcion').value = paquete.descripcion;
            document.getElementById('paquete-precio').value = paquete.monto_total;
        } catch (error) {
            alert('Error al cargar paquete: ' + error.message);
            return;
        }
    } else {
        title.textContent = 'Nuevo Paquete';
    }

    modal.show();
}

async function savePaquete() {
    const nombre = document.getElementById('paquete-nombre').value;
    const descripcion = document.getElementById('paquete-descripcion').value;
    const monto_total = parseFloat(document.getElementById('paquete-precio').value);

    const data = { nombre, descripcion, monto_total };

    try {
        if (currentPaqueteId) {
            await CatalogoService.update(currentPaqueteId, data);
        } else {
            await CatalogoService.create(data);
        }

        const modalEl = document.getElementById('paqueteModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();
        loadView('catalogo');

    } catch (error) {
        alert('Error al guardar paquete: ' + error.message);
    }
}

async function deletePaquete(id) {
    if (confirm('¿Estás seguro de eliminar este paquete?')) {
        try {
            await CatalogoService.delete(id);
            loadView('catalogo');
        } catch (error) {
            alert('Error al eliminar paquete: ' + error.message);
        }
    }
}

// Contratacion Actions
async function contratarPaquete(id, nombre, precio, tipoEventoId, tipoEventoNombre) {
    console.log("Contratar paquete:", id, nombre, precio, tipoEventoId);

    document.getElementById('contratar-paquete-id').value = id;
    document.getElementById('contratar-paquete-nombre').textContent = nombre;
    document.getElementById('contratar-paquete-precio').textContent = precio.toFixed(2);

    document.getElementById('evento-tipo').value = tipoEventoId;

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('evento-fecha').valueAsDate = tomorrow;
    document.getElementById('evento-hora').value = "18:00";

    const modal = new bootstrap.Modal(document.getElementById('contratarModal'));
    modal.show();
}

async function confirmarContratacion() {
    const paqueteId = document.getElementById('contratar-paquete-id').value;
    const tipoEventoId = document.getElementById('evento-tipo').value;
    const fecha = document.getElementById('evento-fecha').value;
    const hora = document.getElementById('evento-hora').value;
    const ubicacion = document.getElementById('evento-ubicacion').value;
    const invitados = parseInt(document.getElementById('evento-invitados').value);

    if (!tipoEventoId || tipoEventoId === 'null' || tipoEventoId === 'undefined') {
        console.warn("Warning: tipoEventoId is missing");
    }

    if (!fecha || !hora || !ubicacion) {
        alert('Por favor completa todos los campos obligatorios');
        return;
    }

    try {
        await ContratacionService.crearPedido({
            paquete_id: paqueteId,
            tipo_evento_id: tipoEventoId,
            fecha_evento: fecha,
            hora_inicio: hora,
            ubicacion: ubicacion,
            num_personas: invitados
        });

        const modal = bootstrap.Modal.getInstance(document.getElementById('contratarModal'));
        modal.hide();

        alert('¡Pedido creado exitosamente!');
        loadView('pedidos');

    } catch (error) {
        alert('Error al crear el pedido: ' + error.message);
    }
}

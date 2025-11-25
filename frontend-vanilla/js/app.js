// js/app.js
import { Auth } from "./auth.js";
import { IAM, CATALOGO, getToken } from "./api.js";
import { PROVEEDORES, CONTRATACION } from "./services.js";
import { verifyAllServices, resultsToHtml } from "./healthcheck.js";

console.log("[app] module loaded");

// Inject small stylesheet for catalog card sizing & hover
const _injectCatalogStyles = (() => {
  try {
    const css = `
      /* Catalog cards: uniform height and nice hover */
      .catalog-card { height: 100%; }
      .catalog-card .card-body { display: flex; flex-direction: column; min-height: 200px; }
      .catalog-card .card-price { min-height: 48px; }
      .catalog-card .card-footer-cta { margin-top: auto; }
      .catalog-card:hover { transform: translateY(-4px); transition: transform 160ms ease; }
    `;
    const s = document.createElement('style');
    s.setAttribute('type', 'text/css');
    s.appendChild(document.createTextNode(css));
    document.head.appendChild(s);
  } catch (e) {
    /* noop */
  }
})();

let currentUser = null; // cache

// Admin pagination state
let adminLimit = 10;
let adminOffset = 0;
let adminTotal = null; // if backend provides total count

// Contratación pendiente (cuando viene desde catálogo sin login)
let pendingPaqueteId = null;

// Proveedor
let proveedorSeleccionado = null;
let reservasActivas = [];
let crearReservaModal = null;

// ----- refs de vistas -----
const views = {
  home: document.getElementById("view-home"),
  catalogo: document.getElementById("view-catalogo"),
  login: document.getElementById("view-login"),
  adminRegister: document.getElementById("view-admin-register"),
  me: document.getElementById("view-me"),
  admin: document.getElementById("view-admin"),
  proveedores: document.getElementById("view-proveedores"),
  contratacion: document.getElementById("view-contratacion"),
};

// ----- navbar -----
const navLogin = document.getElementById("nav-login");
const navCatalogo = document.getElementById("nav-catalogo");
const navLogout = document.getElementById("nav-logout");
const navRegister = document.getElementById("nav-register");
const navAdmin = document.getElementById("nav-admin");
const navProveedores    = document.getElementById("nav-proveedores");
const openPublicRegister = document.getElementById("open-public-register");

// Safety: ensure navbar links trigger routing even if default hashchange is blocked
function bindNavLink(id, hash) {
  const el = document.getElementById(id);
  if (!el) {
    console.log(`[app] nav element not found: ${id}`);
    return;
  }
  el.addEventListener("click", (ev) => {
    ev.preventDefault();
    // solo cambiamos el hash; el listener hashchange llamará router()
    if (location.hash !== hash) {
      location.hash = hash;
    }
  });
}
bindNavLink("nav-catalogo", "#/catalogo");
bindNavLink("nav-proveedores", "#/proveedores");
bindNavLink("nav-contratacion", "#/contratacion");

// Botón para ejecutar verificación de servicios (modo local)
const btnVerifyServices = document.getElementById('btn-verify-services');
if (btnVerifyServices) {
  btnVerifyServices.addEventListener('click', async (ev) => {
    ev.preventDefault();
    const modalEl = document.getElementById('servicesVerificationModal');
    if (!modalEl || !window.bootstrap?.Modal) {
      alert('No se pudo abrir la verificación (modal no disponible)');
      return;
    }

    const modal = new bootstrap.Modal(modalEl);
    const body = document.getElementById('services-verification-body');
    if (body) {
      body.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div><div class="small text-muted mt-2">Ejecutando comprobaciones...</div></div>';
    }
    modal.show();

    try {
      const results = await verifyAllServices();
      if (body) body.innerHTML = resultsToHtml(results);
    } catch (err) {
      console.error('Error verificando servicios', err);
      if (body) body.innerHTML = `<div class="alert alert-danger">Error ejecutando comprobaciones: ${escapeHtml(err?.message || String(err))}</div>`;
    }
  });
}

// Modal público (se inicializa on-demand)
let publicRegisterModal = null;
function ensurePublicModal() {
  if (!publicRegisterModal) {
    const el = document.getElementById("publicRegisterModal");
    if (el && window.bootstrap?.Modal) {
      publicRegisterModal = new bootstrap.Modal(el);
    }
  }
}

// ----- helpers -----
function show(id) {
  Object.values(views).forEach((v) => v?.classList.add("d-none"));
  (views[id] ?? views.home)?.classList.remove("d-none");
  try {
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch {}
}
const roleOf = (u) => (u?.role || "").toString().toUpperCase();
const userRole = () => roleOf(currentUser);

// Escapa texto simple para evitar inyección en templates (muy básico)
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
// Currency helpers (global) used by multiple views
function currencySymbol(code) {
  if (!code) return 'S/';
  const c = String(code).toUpperCase();
  if (c === 'PEN' || c === 'PEN-S' || c === 'PESO') return 'S/';
  if (c === 'USD' || c === 'US' || c === 'DOLAR' || c === 'USD$') return '$';
  return c + ' ';
}

function formatAmount(amount, currency) {
  try {
    return new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount);
  } catch (e) {
    return Number(amount).toFixed(2);
  }
}

// Builder común para el payload de CrearPedidoDesdePaquete
function buildPedidoPayload({
  paquete_id,
  fecha_evento,
  hora_inicio,
  hora_fin,
  ubicacion,
}) {
  const today = new Date();
  const defaultFecha = today.toISOString().slice(0, 10); // YYYY-MM-DD

  const payload = {
    paquete_id: String(paquete_id || "").trim(),
    fecha_evento: (fecha_evento || defaultFecha).toString(),
    hora_inicio: (hora_inicio || "18:00:00").toString(),
    ubicacion: (ubicacion || "Por definir").toString(),
  };

  if (hora_fin) {
    payload.hora_fin = hora_fin.toString();
  }

  if (window.crypto?.randomUUID) {
    const uuid = crypto.randomUUID();
    payload.request_id = uuid;
    payload.correlation_id = uuid;
  }

  return payload;
}

// ====== PERFIL ======
async function loadMe() {
  const pre = document.getElementById("me-json");
  const nameEl = document.getElementById("me-name");
  const emailEl = document.getElementById("me-email");
  const idEl = document.getElementById("me-id");
  const telEl = document.getElementById("me-telefono");
  const roleEl = document.getElementById("me-role");
  const statusEl = document.getElementById("me-status");
  const avatarEl = document.getElementById("me-avatar");

  try {
    const u = await Auth.me();
    currentUser = u;
    if (pre) pre.textContent = JSON.stringify(u, null, 2);

    const nombre = u.nombre || "";
    const email = u.email || "";
    const role = roleOf(u);
    const tel = u.telefono || "—";
    const activo = Number(u.status) === 1;

    const initials = (() => {
      const base = (nombre || email.split("@")[0] || "").trim();
      const parts = base.split(/\s+/);
      const a = (parts[0]?.[0] || "").toUpperCase();
      const b = (parts[1]?.[0] || "").toUpperCase();
      return (a + b) || a || "?";
    })();

    if (avatarEl) avatarEl.textContent = initials;
    if (nameEl) nameEl.textContent = nombre || email;
    if (emailEl) emailEl.textContent = email;
    if (idEl) idEl.textContent = u.id || "—";
    if (telEl) telEl.textContent = tel;
    if (roleEl) {
      roleEl.textContent = role || "—";
      roleEl.className =
        "ms-auto badge rounded-pill " +
        (role === "ADMIN" ? "text-bg-primary" : "text-bg-info");
    }
    if (statusEl) {
      statusEl.textContent = activo ? "ACTIVO" : "INACTIVO";
      statusEl.className =
        "badge rounded-pill " +
        (activo ? "text-bg-success" : "text-bg-secondary");
    }
  } catch (e) {
    if (pre) {
      pre.classList.remove("d-none");
      pre.textContent = "Error: " + e.message;
    }
  }
}

// ====== CONTRATACIÓN DESDE CATÁLOGO ======
function solicitarContratacionDesdeCatalogo(paquete) {
    const paqueteId = paquete.id ?? paquete.codigo ?? paquete.code;
    if (!paqueteId) {
        alert("No se puede contratar este paquete (falta ID).");
        return;
    }

    if (!Auth.token) {
        pendingPaqueteId = paqueteId;
        location.hash = "/login";
        return;
    }

    // Mostrar modal/formulario para completar datos del evento
    showContratacionModal(paqueteId, paquete);
}

async function showContratacionModal(paqueteId, paquete) {
    // Obtener servicios del paquete
    const servicios = paquete?.items || paquete?.servicios || [];
    
    // Crear HTML para selección de proveedores por servicio
    let serviciosHTML = '';
    if (servicios.length > 0) {
        serviciosHTML = `
            <div class="mb-4">
                <h6 class="mb-3">
                    <i class="bi bi-person-check me-2"></i>Seleccionar Proveedores (Opcional)
                </h6>
                <small class="text-muted d-block mb-3">
                    Puedes elegir proveedores específicos para cada servicio. 
                    Si no eliges, nuestro equipo asignará los mejores disponibles.
                </small>
                <div id="servicios-proveedores-container" class="border rounded p-3 bg-light">
                    <div class="text-center">
                        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                        <p class="small text-muted mt-2">Cargando proveedores disponibles...</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    const modalHtml = `
        <div class="modal fade" id="contratacionModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary-subtle">
                        <h5 class="modal-title">
                            <i class="bi bi-calendar-event me-2"></i>Reservar: ${escapeHtml(paquete?.nombre || 'Paquete')}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="contratacion-modal-form">
                            <h6 class="mb-3">
                                <i class="bi bi-info-circle me-2"></i>Datos del Evento
                            </h6>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Fecha del evento</label>
                                    <input type="date" name="fecha_evento" class="form-control" required 
                                           min="${new Date().toISOString().split('T')[0]}"
                                           id="fecha-evento-input">
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Hora de inicio</label>
                                    <input type="time" name="hora_inicio" class="form-control" required value="18:00">
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Hora de fin</label>
                                    <input type="time" name="hora_fin" class="form-control" placeholder="Opcional">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Ubicación</label>
                                <input type="text" name="ubicacion" class="form-control" required 
                                       placeholder="Dirección del evento (ej: Salón Los Jardines, Lima)">
                            </div>
                            
                            ${serviciosHTML}
                            
                            <input type="hidden" name="paquete_id" value="${paqueteId}">
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" id="confirmar-contratacion">
                            <i class="bi bi-check-circle me-2"></i>Confirmar Reserva
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remover modal existente si hay
    const existingModal = document.getElementById('contratacionModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modalElement = document.getElementById('contratacionModal');
    const modal = new bootstrap.Modal(modalElement);

    // Cargar proveedores cuando se selecciona fecha
    const fechaInput = document.getElementById('fecha-evento-input');
    if (fechaInput && servicios.length > 0) {
        fechaInput.addEventListener('change', async () => {
            const fecha = fechaInput.value;
            if (fecha) {
                await cargarProveedoresParaServicios(servicios, fecha, paquete);
            }
        });
    }

    // Configurar evento de confirmación
    document.getElementById('confirmar-contratacion').addEventListener('click', async () => {
        const form = document.getElementById('contratacion-modal-form');
        const formData = new FormData(form);
        
        const payload = {
            paquete_id: formData.get('paquete_id'),
            fecha_evento: formData.get('fecha_evento'),
            hora_inicio: formData.get('hora_inicio'),
            hora_fin: formData.get('hora_fin') || undefined,
            ubicacion: formData.get('ubicacion')
        };

        // Validaciones básicas
        if (!payload.fecha_evento || !payload.hora_inicio || !payload.ubicacion) {
            showNotification('Por favor complete todos los campos requeridos', 'warning');
            return;
        }

        // Recopilar proveedores seleccionados
        const proveedoresSeleccionados = [];
        servicios.forEach((servicio, idx) => {
            const selectEl = document.getElementById(`proveedor-select-${idx}`);
            if (selectEl && selectEl.value) {
                proveedoresSeleccionados.push({
                    opcion_servicio_id: servicio.opcion_servicio_id || servicio.id,
                    proveedor_id: selectEl.value
                });
            }
        });

        // Agregar proveedores al payload si hay seleccionados
        if (proveedoresSeleccionados.length > 0) {
            payload.proveedores_seleccionados = proveedoresSeleccionados;
        }

        try {
            modal.hide();
            await doContratarPaquete(payload);
        } catch (error) {
            console.error('Error en contratación:', error);
            showNotification('Error al crear la reserva: ' + (error.message || error), 'error');
        }
    });

    modal.show();
    
    // Limpiar modal cuando se cierre
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.remove();
    });
}

// Función para cargar proveedores disponibles por servicio
async function cargarProveedoresParaServicios(servicios, fecha, paquete) {
    const container = document.getElementById('servicios-proveedores-container');
    if (!container) return;

    container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div><p class="small mt-2">Cargando proveedores...</p></div>';

    try {
        // Para cada servicio, buscar proveedores disponibles
        const serviciosHTML = [];
        
        for (let idx = 0; idx < servicios.length; idx++) {
            const servicio = servicios[idx];
            const servicioId = servicio.opcion_servicio_id || servicio.servicio_id || servicio.id;
            const nombre = servicio.nombre_servicio || servicio.nombre || servicio.name || `Servicio ${idx + 1}`;
            
            try {
                // Consultar proveedores disponibles
                const proveedores = await PROVEEDORES.buscarDisponibles(servicioId, fecha, 20, 0);
                const lista = Array.isArray(proveedores) ? proveedores : proveedores?.items ?? [];
                
                let opcionesHTML = '<option value="">Sin asignar (Admin asignará después)</option>';
                
                if (lista.length > 0) {
                    // Ordenar por rating descendente
                    lista.sort((a, b) => (Number(b.rating_prom || 0) - Number(a.rating_prom || 0)));
                    
                    opcionesHTML += lista.map(prov => {
                        const rating = Number(prov.rating_prom || 0).toFixed(1);
                        const stars = '⭐'.repeat(Math.round(rating));
                        const precio = prov.precio_referencia ? ` - S/ ${prov.precio_referencia}` : '';
                        return `<option value="${prov.id}">${escapeHtml(prov.nombre || prov.name || prov.id)} ${stars}${precio}</option>`;
                    }).join('');
                } else {
                    opcionesHTML += '<option value="" disabled>No hay proveedores disponibles</option>';
                }
                
                serviciosHTML.push(`
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">
                            <i class="bi bi-geo-alt me-1"></i>${escapeHtml(nombre)}
                        </label>
                        <select class="form-select form-select-sm" id="proveedor-select-${idx}">
                            ${opcionesHTML}
                        </select>
                    </div>
                `);
            } catch (e) {
                console.error(`Error cargando proveedores para servicio ${servicioId}:`, e);
                serviciosHTML.push(`
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">${escapeHtml(nombre)}</label>
                        <select class="form-select form-select-sm" id="proveedor-select-${idx}" disabled>
                            <option>Error al cargar proveedores</option>
                        </select>
                    </div>
                `);
            }
        }
        
        container.innerHTML = serviciosHTML.join('');
        
    } catch (error) {
        console.error('Error cargando proveedores:', error);
        container.innerHTML = `
            <div class="alert alert-warning small mb-0">
                <i class="bi bi-exclamation-triangle me-2"></i>
                No se pudieron cargar los proveedores. Podrás asignarlos después.
            </div>
        `;
    }
}

// Modificar doContratarPaquete para aceptar el payload completo
async function doContratarPaquete(payload) {
    try {
        // Usar buildPedidoPayload para agregar request_id, etc.
        const fullPayload = buildPedidoPayload(payload);
        console.log("📤 Enviando payload:", fullPayload);
        
        const creado = await CONTRATACION.crearPedido(fullPayload);
        console.log("[contratacion] pedido creado desde catálogo", creado);
        alert("¡Pedido registrado correctamente! Revisa tu sección de contrataciones.");
        location.hash = "/contratacion";
    } catch (e) {
        console.error("Error al crear pedido desde catálogo", e);
        alert("No se pudo registrar la contratación: " + (e.message || e));
    }
}
async function runPendingContratacion() {
  if (!pendingPaqueteId) return false;
  const id = pendingPaqueteId;
  pendingPaqueteId = null;
  // doContratarPaquete expects a payload object — provide paquete_id
  await doContratarPaquete({ paquete_id: id });
  return true;
}

// ====== CATÁLOGO ======
// Renderiza tarjetas y carrusel a partir de la lista de paquetes.
async function loadCatalogo() {
  const alertBox = document.getElementById("catalogo-alert");
  const cardsRow = document.getElementById("catalogo-cards");
  const carouselWrap = document.getElementById("catalogo-carousel-wrapper");
  const carouselInner = document.getElementById("catalogo-carousel-inner");
  const reloadBtn = document.getElementById("btn-catalogo-reload");

  if (!cardsRow) return; // vista no presente

  // estado inicial UI
  if (alertBox) {
    alertBox.className = "alert alert-info";
    alertBox.textContent = "Cargando catálogo...";
    alertBox.classList.remove("d-none");
  }
  if (reloadBtn) reloadBtn.disabled = true;
  cardsRow.innerHTML = "";
  if (carouselInner) carouselInner.innerHTML = "";
  if (carouselWrap) carouselWrap.classList.add("d-none");

  try {
  const paquetes = await CATALOGO.paquetes();
  const list = Array.isArray(paquetes) ? paquetes : paquetes?.items ?? [];

  // cache for client-side filtering
  window.__cachedCatalogoPaquetes = list;

  // ensure filter UI exists and is wired
  try { ensureCatalogFilters(); } catch(e) { console.error('Error inicializando filtros', e); }

  // apply any currently selected filters before rendering
  const activeFilters = getActiveCatalogFilters();
  const filteredList = applyCatalogFiltersToList(list, activeFilters);

    if (!list.length) {
      if (alertBox) {
        alertBox.className = "alert alert-warning";
        alertBox.textContent = "No hay paquetes configurados en el catálogo.";
        alertBox.classList.remove("d-none");
      }
      return;
    }

    if (alertBox) alertBox.classList.add("d-none");

    // --- Tarjetas estilo grid / watchlist ---
    const fragment = document.createDocumentFragment();
  filteredList.forEach((p, idx) => {
      const col = document.createElement("div");
      col.className = "col-12 col-md-6 col-lg-4";

      // create card skeleton early so we can append pieces in order
      const card = document.createElement("div");
      card.className = "card mb-3 shadow-sm position-relative"; // position-relative for price badge

  const body = document.createElement("div");
  body.className = "card-body";
  // make body a flex column so footer CTA can be pushed to bottom
  body.classList.add('d-flex', 'flex-column');

      const title = document.createElement("h5");
      title.className = "card-title mb-1";
      title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;

      const desc = document.createElement("p");
      desc.className = "card-text small text-muted mb-2";
      desc.textContent = p.descripcion || p.description || "Sin descripción.";

  const footer = document.createElement("div");
  // use mt-auto via class to push footer to bottom of the card body
  footer.className = "mt-3 mt-auto d-flex justify-content-between align-items-center small gap-2 card-footer-cta";

      // Price resolution: support direct fields or nested precio_paquete table (object or array)
      function resolvePrice(obj) {
        if (!obj) return null;

        // Direct simple fields (include monto_total which catalogo returns)
        const direct = obj.monto_total ?? obj.monto ?? obj.precio ?? obj.precio_min ?? obj.precio_unitario ?? obj.amount ?? obj.price ?? null;
        if (direct != null && !Number.isNaN(Number(direct))) {
          return { amount: Number(direct), currency: obj.moneda ?? obj.currency ?? 'PEN' };
        }

        // Nested precio_paquete (may be an object or an array)
        const pp = obj.precio_paquete ?? obj.precio_paquetes ?? obj.precios ?? obj.price_list ?? null;
        if (pp) {
          const rows = Array.isArray(pp) ? pp.slice() : [pp];
          // prefer active (vigente_hasta null) or latest by vigente_desde
          let sel = rows.find(r => r.vigente_hasta == null) || rows.sort((a,b) => new Date(b.vigente_desde) - new Date(a.vigente_desde))[0];
          if (sel) {
            const m = sel.monto ?? sel.amount ?? sel.price ?? null;
            const c = sel.moneda ?? sel.currency ?? obj.moneda ?? 'PEN';
            if (m != null && !Number.isNaN(Number(m))) return { amount: Number(m), currency: c };
          }
        }

        return null;
      }

      const priceInfo = resolvePrice(p);

      // helper to map currency code -> symbol
      function currencySymbol(code) {
        if (!code) return 'S/';
        const c = String(code).toUpperCase();
        if (c === 'PEN' || c === 'PEN-S' || c === 'PESO') return 'S/';
        if (c === 'USD' || c === 'US' || c === 'DOLAR' || c === 'USD$') return '$';
        return c + ' ';
      }

      // format amount with thousands separators according to locale
      function formatAmount(amount, currency) {
        try {
          return new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount);
        } catch (e) {
          return Number(amount).toFixed(2);
        }
      }

      // Price badge top-right
      const priceBadge = document.createElement("div");
      priceBadge.className = "position-absolute top-0 end-0 m-2 badge rounded-pill";
      if (priceInfo && priceInfo.amount != null) {
        priceBadge.classList.add( "text-white");
        priceBadge.style.fontSize = "0.95rem";
  priceBadge.textContent = `${currencySymbol(priceInfo.currency)}${formatAmount(priceInfo.amount, priceInfo.currency)}`;
      } else {
        priceBadge.classList.add("bg-secondary", "text-white");
        priceBadge.style.fontSize = "0.85rem";
        priceBadge.textContent = "Consultar precio";
      }

      // prominent price in the body (large but balanced)
      const priceBox = document.createElement("div");
      priceBox.className = "mb-2 d-flex align-items-baseline gap-2";
      const priceMain = document.createElement("div");
      priceMain.className = "h5 fw-bold mb-0";
      if (priceInfo && priceInfo.amount != null) {
        priceMain.classList.add("text-success");
        priceMain.textContent = `Desde ${currencySymbol(priceInfo.currency)}${formatAmount(priceInfo.amount, priceInfo.currency)}`;
      } else {
        //priceMain.classList.add("text-secondary");
        priceMain.textContent = "Precio a consultar";
      }
      priceBox.appendChild(priceMain);

      // Ensure there's a dedicated price container in the card for consistent layout
      const priceContainer = document.createElement("div");
      priceContainer.className = "card-price mb-2"; // CSS hook: keep place for price even if empty
      priceContainer.setAttribute('role', 'text');
      priceContainer.appendChild(priceBox);

      const codeBadge = document.createElement("span");
      codeBadge.className = "badge text-bg-primary ms-auto";
      codeBadge.textContent = p.codigo || p.code || p.id || `PK-${idx + 1}`;

      // meta (servicios)
      const meta = document.createElement("div");
      //meta.className = "mt-2 small text-muted";
      const servicios = p.servicios || p.services || [];
      if (Array.isArray(servicios) && servicios.length) {
        const snippet = servicios.slice(0, 2).map(s => s.nombre || s.name || String(s)).join(', ');
        meta.textContent = `Incluye: ${snippet}` + (servicios.length > 2 ? ` +${servicios.length - 2} más` : '');
      } else {
        meta.textContent = "Servicios no detallados.";
      }

      // CTA
      const cta = document.createElement("div");
      cta.className = "d-flex gap-2 align-items-center";

      // Ver detalle button (secondary)
      const verBtn = document.createElement('button');
      verBtn.className = 'btn btn-sm btn-outline-secondary';
      verBtn.textContent = 'Ver detalle';
      verBtn.addEventListener('click', (ev) => {
        ev.preventDefault();
        showPaqueteDetalle(p);
      });

      const btn = document.createElement("button");
      btn.className = "btn btn-sm btn-primary";
      btn.textContent = "Reservar / Contratar";
      btn.addEventListener("click", () => solicitarContratacionDesdeCatalogo(p));

      cta.appendChild(verBtn);
      cta.appendChild(btn);

      // assemble
  body.appendChild(title);
  body.appendChild(desc);
  body.appendChild(priceContainer);
      body.appendChild(meta);
      footer.appendChild(codeBadge);
      footer.appendChild(cta);
      body.appendChild(footer);

      card.appendChild(body);
      card.appendChild(priceBadge);
      col.appendChild(card);
      fragment.appendChild(col);
    });
    cardsRow.appendChild(fragment);

    // --- Carrusel basado en los mismos paquetes (resumen) ---
    if (carouselInner && carouselWrap) {
      filteredList.forEach((p, idx) => {
        const item = document.createElement("div");
        item.className = "carousel-item" + (idx === 0 ? " active" : "");

        const inner = document.createElement("div");
        inner.className =
          "d-flex flex-column flex-md-row align-items-stretch p-4 bg-white border rounded-3 shadow-sm gap-3";
        inner.style.minHeight = "160px";

        const left = document.createElement("div");
        left.className = "flex-grow-1";

        const title = document.createElement("h5");
        title.className = "mb-1";
        title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;

        const desc = document.createElement("p");
        desc.className = "mb-2 small text-muted";
        desc.textContent =
          p.descripcion || p.description || "Sin descripción.";

        const meta = document.createElement("div");
        meta.className = "small text-secondary";
        const servicios = p.servicios || p.services || [];
        if (Array.isArray(servicios) && servicios.length) {
          meta.textContent = `Incluye ${servicios.length} servicio(s).`;
        } else {
          meta.textContent = "Servicios no detallados.";
        }

        left.appendChild(title);
        left.appendChild(desc);
        left.appendChild(meta);

        const right = document.createElement("div");
        right.className =
          "d-flex flex-column justify-content-end align-items-end";

        const price = document.createElement("div");
        const monto = p.precio ?? p.monto ?? p.amount;
        //price.className = "fw-semibold mb-2";
        //if (monto != null && !Number.isNaN(Number(monto))) {
        //  price.textContent = `Desde S/ ${Number(monto).toFixed(2)}`;
        //} else {
        //  price.textContent = "Precio a consultar";
        //}

        const cta = document.createElement("button");
        cta.className = "btn btn-sm btn-outline-primary";
        cta.textContent = "Contratar ahora";
        cta.addEventListener("click", () =>
          solicitarContratacionDesdeCatalogo(p)
        );

        right.appendChild(price);
        right.appendChild(cta);

        inner.appendChild(left);
        inner.appendChild(right);
        item.appendChild(inner);
        carouselInner.appendChild(item);
      });

      if (filteredList.length > 1) {
        carouselWrap.classList.remove("d-none");
      } else {
        carouselWrap.classList.add("d-none");
      }
    }
      await loadCatalogoMeta();
  } catch (err) {
    console.error("Error cargando catálogo", err);
    if (alertBox) {
      alertBox.className = "alert alert-danger";
      alertBox.textContent =
        "No se pudo cargar el catálogo. Intenta más tarde.";
      alertBox.classList.remove("d-none");
    }
  } finally {
    const reloadBtn2 = document.getElementById("btn-catalogo-reload");
    if (reloadBtn2) reloadBtn2.disabled = false;
  }
}

// ---- FILTROS CLIENT-SIDE ----
// List provided by the user (event types / service tags)
const CATALOG_FILTERS = [
  "Boda", "Matrimonio", "Cena de gala", "Conferencia", "Congreso", "Feria", "Convención",
  "Exposición", "Lanzamiento de producto", "Concierto", "Festival", "Evento deportivo",
  "Desfile", "Reunión corporativa", "Inauguración", "Cocktail", "Cumpleaños", "Aniversario",
  "Baby shower", "Bautizo", "Primera comunión", "Grados", "Promoción", "Cena privada",
  "Team building", "Capacitación", "Workshop", "Seminario", "Webinar", "Pixels", "Stand",
  "Decoración", "Ambientación", "Audiovisuales", "Sonido", "Iluminación", "Fotografía", "Video",
  "Catering", "Banquete", "Bar", "Mixología", "Torta", "Mesa de postres", "Mobiliario",
  "Transporte", "Logística", "Seguridad", "Recepción", "Hostess", "Animación", "Show",
  "Maestro de ceremonias", "DJ", "Banda en vivo", "Artista", "Montaje", "Desmontaje", "Limpieza",
  "Invitaciones", "Registro", "Control de acceso", "Streaming", "Traducción simultánea", "Tarimas",
  "Escenografía", "Pantallas", "Proyección", "Publicidad", "Merchandising", "Merch", "Photobooth"
];

function ensureCatalogFilters() {
  const container = document.getElementById('catalogo-filters');
  if (!container) return;
  if (container._initialized) return;

  // Build nested combobox UI: Tipo Evento (searchable) -> Servicio (searchable, filtered)
  const row = document.createElement('div');
  row.className = 'd-flex flex-column flex-md-row gap-2 align-items-start';

  // Tipo evento select + Servicio select (enhanced with TomSelect when available)
  const tipoWrap = document.createElement('div');
  tipoWrap.className = 'flex-grow-1';
  const tipoLabel = document.createElement('label');
  tipoLabel.className = 'form-label small mb-1';
  tipoLabel.textContent = 'Tipo de evento';
  const tipoSelect = document.createElement('select');
  tipoSelect.className = 'form-select form-select-sm';
  tipoSelect.id = 'catalogo-filter-tipo-select';
  tipoWrap.appendChild(tipoLabel);
  tipoWrap.appendChild(tipoSelect);

  // Servicio select
  const servicioWrap = document.createElement('div');
  servicioWrap.className = 'flex-grow-1';
  const servicioLabel = document.createElement('label');
  servicioLabel.className = 'form-label small mb-1';
  servicioLabel.textContent = 'Tipo de servicio';
  const servicioSelect = document.createElement('select');
  servicioSelect.className = 'form-select form-select-sm';
  servicioSelect.id = 'catalogo-filter-servicio-select';
  servicioWrap.appendChild(servicioLabel);
  servicioWrap.appendChild(servicioSelect);

  // Controls (clear only; filtering is live)
  const controlsWrap = document.createElement('div');
  controlsWrap.className = 'd-flex flex-column gap-1';
  const clearBtn2 = document.createElement('button');
  clearBtn2.type = 'button';
  clearBtn2.className = 'btn btn-sm btn-outline-secondary';
  clearBtn2.textContent = 'Limpiar';
  controlsWrap.appendChild(clearBtn2);

  // active count
  const count = document.createElement('div');
  count.id = 'catalogo-filters-count';
  count.className = 'small text-secondary mt-1';
  controlsWrap.appendChild(count);

  row.appendChild(tipoWrap);
  row.appendChild(servicioWrap);
  row.appendChild(controlsWrap);

  container.appendChild(row);

  // fill datalists using meta when available, otherwise fall back to static tags
  function populateTipoOptions() {
    const tipos = window.__catalogMetaTipos || CATALOG_FILTERS.map(x => ({ nombre: x, id: x }));
    // if TomSelect is available, use it, otherwise populate the <select>
    const selectEl = document.getElementById('catalogo-filter-tipo-select');
    if (window.__catalogoTipoTS && typeof window.__catalogoTipoTS.clearOptions === 'function') {
      window.__catalogoTipoTS.clearOptions();
      tipos.forEach(t => {
        const val = t.nombre || t.name || String(t.id || t);
        window.__catalogoTipoTS.addOption({ value: val, text: val });
      });
      window.__catalogoTipoTS.refreshOptions(false);
    } else if (selectEl) {
      selectEl.innerHTML = '';
      tipos.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.nombre || t.name || String(t.id || t);
        opt.textContent = t.nombre || t.name || String(t.id || t);
        selectEl.appendChild(opt);
      });
    }
  }

  function populateServicioOptions(selectedTipo) {
    const servicios = window.__catalogMetaServicios || [];
    let list = servicios || [];
    if (selectedTipo) {
      const sel = selectedTipo.toString().toLowerCase();
      list = servicios.filter(s => String(s.tipo_evento_id || s.tipo_id || '').toLowerCase() === sel || (s.tipo_nombre || s.tipo || '').toString().toLowerCase().includes(sel) || (s.nombre || s.name || '').toString().toLowerCase().includes(sel));
      if (!list.length) {
        list = servicios.filter(s => (s.nombre || s.name || '').toString().toLowerCase().includes(sel));
      }
    }

    const selectEl = document.getElementById('catalogo-filter-servicio-select');
    if (!list.length && (!window.__catalogMetaServicios || !window.__catalogMetaServicios.length)) {
      // fallback static tags
      if (window.__catalogoServicioTS && typeof window.__catalogoServicioTS.clearOptions === 'function') {
        window.__catalogoServicioTS.clearOptions();
        (CATALOG_FILTERS || []).forEach(lbl => window.__catalogoServicioTS.addOption({ value: lbl, text: lbl }));
        window.__catalogoServicioTS.refreshOptions(false);
      } else if (selectEl) {
        selectEl.innerHTML = '';
        (CATALOG_FILTERS || []).forEach(lbl => {
          const opt = document.createElement('option'); opt.value = lbl; opt.textContent = lbl; selectEl.appendChild(opt);
        });
      }
      return;
    }

    if (window.__catalogoServicioTS && typeof window.__catalogoServicioTS.clearOptions === 'function') {
      window.__catalogoServicioTS.clearOptions();
      list.forEach(s => {
        const val = s.nombre || s.name || s.id || '';
        window.__catalogoServicioTS.addOption({ value: val, text: val });
      });
      window.__catalogoServicioTS.refreshOptions(false);
    } else if (selectEl) {
      selectEl.innerHTML = '';
      list.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.nombre || s.name || s.id || '';
        opt.textContent = s.nombre || s.name || s.id || '';
        selectEl.appendChild(opt);
      });
    }
  }

  // events: live filtering while selecting
  function onTipoChange(val) {
    populateServicioOptions(val);
    rerenderCatalogWithFilters(getActiveCatalogFilters());
  }

  function onServicioChange() {
    rerenderCatalogWithFilters(getActiveCatalogFilters());
  }

  // wire enhanced controls (TomSelect) if available
  try {
    const tipoSel = document.getElementById('catalogo-filter-tipo-select');
    const servSel = document.getElementById('catalogo-filter-servicio-select');
    if (window.TomSelect) {
      if (window.__catalogoTipoTS) try { window.__catalogoTipoTS.destroy(); } catch (e) {}
      if (window.__catalogoServicioTS) try { window.__catalogoServicioTS.destroy(); } catch (e) {}

      window.__catalogoTipoTS = new TomSelect(tipoSel, {
        valueField: 'value', labelField: 'text', searchField: ['text'], maxItems: 1,
        create: false, placeholder: 'Buscar tipo de evento...', allowEmptyOption: true
      });
      window.__catalogoServicioTS = new TomSelect(servSel, {
        valueField: 'value', labelField: 'text', searchField: ['text'], maxItems: 1,
        create: false, placeholder: 'Buscar tipo de servicio...', allowEmptyOption: true
      });

      window.__catalogoTipoTS.on('change', v => onTipoChange(v));
      window.__catalogoServicioTS.on('change', v => onServicioChange());
    } else {
      // fallback to native select/input
      const tipoNative = document.getElementById('catalogo-filter-tipo-select');
      const servNative = document.getElementById('catalogo-filter-servicio-select');
      if (tipoNative) tipoNative.addEventListener('input', (e) => onTipoChange(e.target.value || ''));
      if (servNative) servNative.addEventListener('input', onServicioChange);
    }
  } catch (e) {
    console.error('Error inicializando TomSelect para filtros', e);
  }

  // clear button
  clearBtn2.addEventListener('click', () => {
    try {
      if (window.__catalogoTipoTS) window.__catalogoTipoTS.clear(true);
      if (window.__catalogoServicioTS) window.__catalogoServicioTS.clear(true);
    } catch (e) {
      const t = document.getElementById('catalogo-filter-tipo-select'); if (t) t.value = '';
      const s = document.getElementById('catalogo-filter-servicio-select'); if (s) s.value = '';
    }
    populateServicioOptions('');
    rerenderCatalogWithFilters({});
  });

  // initial population
  populateTipoOptions();
  populateServicioOptions('');

  container._initialized = true;
}

function getActiveCatalogFilters() {
  let tipo = '';
  let servicio = '';
  try {
    if (window.__catalogoTipoTS && typeof window.__catalogoTipoTS.getValue === 'function') {
      tipo = window.__catalogoTipoTS.getValue() || '';
    } else {
      tipo = (document.getElementById('catalogo-filter-tipo-select') || {}).value || '';
    }
    if (window.__catalogoServicioTS && typeof window.__catalogoServicioTS.getValue === 'function') {
      servicio = window.__catalogoServicioTS.getValue() || '';
    } else {
      servicio = (document.getElementById('catalogo-filter-servicio-select') || {}).value || '';
    }
  } catch (e) {
    tipo = (document.getElementById('catalogo-filter-tipo-select') || {}).value || '';
    servicio = (document.getElementById('catalogo-filter-servicio-select') || {}).value || '';
  }
  const countEl = document.getElementById('catalogo-filters-count');
  const count = (tipo ? 1 : 0) + (servicio ? 1 : 0);
  if (countEl) countEl.textContent = count ? `${count} filtro(s) activos` : '';
  return { tipo: tipo || null, servicio: servicio || null };
}

function applyCatalogFiltersToList(list, activeFilters) {
  if (!activeFilters) return list;
  const tipo = (activeFilters.tipo || '').toString().toLowerCase();
  const servicio = (activeFilters.servicio || '').toString().toLowerCase();
  if (!tipo && !servicio) return list;

  return list.filter(p => {
    let okTipo = true;
    let okServicio = true;

    // Tipo filtering: try structured fields first, otherwise text-search
    if (tipo) {
      okTipo = false;
      // check direct package tipo fields
      if (String(p.tipo_evento_id || p.tipo_id || '').toLowerCase() === tipo) okTipo = true;
      if (!okTipo && String(p.tipo_nombre || p.tipo || '').toLowerCase().includes(tipo)) okTipo = true;
      // check servicios entries
      if (!okTipo && Array.isArray(p.servicios)) {
        okTipo = p.servicios.some(s => String(s.tipo_evento_id || s.tipo_id || '').toLowerCase() === tipo || (s.tipo_nombre || s.tipo || '').toString().toLowerCase().includes(tipo));
      }
      // fallback: search in name/description
      if (!okTipo) {
        const text = ((p.nombre||'') + ' ' + (p.descripcion||'')).toLowerCase();
        if (text.indexOf(tipo) !== -1) okTipo = true;
      }
    }

    if (servicio) {
      okServicio = false;
      // check servicios entries names/ids
      if (Array.isArray(p.servicios)) {
        okServicio = p.servicios.some(s => String(s.id || s.opcion_servicio_id || s.servicio_id || s.nombre || s.name || '').toLowerCase().includes(servicio));
      }
      // check package-level fields
      if (!okServicio) {
        const text = ((p.nombre||'') + ' ' + (p.descripcion||'') + ' ' + JSON.stringify(p.servicios || [])).toLowerCase();
        if (text.indexOf(servicio) !== -1) okServicio = true;
      }
    }

    return okTipo && okServicio;
  });
}

function rerenderCatalogWithFilters(activeFilters) {
  try {
    const all = window.__cachedCatalogoPaquetes || [];
    const filtered = applyCatalogFiltersToList(all, activeFilters);
    // clear current DOM elements and re-render by calling loadCatalogoRender helpers
    // Instead of duplicating rendering code, call a lightweight renderer: we set a flag and call loadCatalogo() but avoid re-fetch
    renderCatalogFromCache(filtered);
  } catch (e) { console.error('Error aplicando filtros', e); }
}

function renderCatalogFromCache(list) {
  // minimal rendering: rebuild cards and carousel using same logic as loadCatalogo but without network calls
  const cardsRow = document.getElementById("catalogo-cards");
  const carouselInner = document.getElementById("catalogo-carousel-inner");
  const carouselWrap = document.getElementById("catalogo-carousel-wrapper");
  if (!cardsRow) return;
  cardsRow.innerHTML = '';
  if (carouselInner) carouselInner.innerHTML = '';
  if (carouselWrap) carouselWrap.classList.add('d-none');

  if (!list || !list.length) {
    const alertBox = document.getElementById('catalogo-alert');
    if (alertBox) {
      alertBox.className = 'alert alert-warning';
      alertBox.textContent = 'No hay paquetes que coincidan con los filtros seleccionados.';
      alertBox.classList.remove('d-none');
    }
    return;
  } else {
    const alertBox = document.getElementById('catalogo-alert');
    if (alertBox) alertBox.classList.add('d-none');
  }

  // reuse existing code paths by temporarily mapping list into the same DOM creation used in loadCatalogo
  // We'll call the same card creation code by emulating the inner forEach used previously.
  const fragment = document.createDocumentFragment();
  list.forEach((p, idx) => {
    const col = document.createElement("div");
    col.className = "col-12 col-md-6 col-lg-4";
    const card = document.createElement("div");
    card.className = "card mb-3 shadow-sm position-relative";
    const body = document.createElement("div");
    body.className = "card-body d-flex flex-column";
    const title = document.createElement("h5");
    title.className = "card-title mb-1";
    title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;
    const desc = document.createElement("p");
    desc.className = "card-text small text-muted mb-2";
    desc.textContent = p.descripcion || p.description || "Sin descripción.";

    // price resolution (reuse small helper from loadCatalogo)
    function resolvePrice(obj) {
      if (!obj) return null;
      const direct = obj.monto_total ?? obj.monto ?? obj.precio ?? obj.precio_min ?? obj.precio_unitario ?? obj.amount ?? obj.price ?? null;
      if (direct != null && !Number.isNaN(Number(direct))) {
        return { amount: Number(direct), currency: obj.moneda ?? obj.currency ?? 'PEN' };
      }
      const pp = obj.precio_paquete ?? obj.precio_paquetes ?? obj.precios ?? obj.price_list ?? null;
      if (pp) {
        const rows = Array.isArray(pp) ? pp.slice() : [pp];
        let sel = rows.find(r => r.vigente_hasta == null) || rows.sort((a,b) => new Date(b.vigente_desde) - new Date(a.vigente_desde))[0];
        if (sel) {
          const m = sel.monto ?? sel.amount ?? sel.price ?? null;
          const c = sel.moneda ?? sel.currency ?? obj.moneda ?? 'PEN';
          if (m != null && !Number.isNaN(Number(m))) return { amount: Number(m), currency: c };
        }
      }
      return null;
    }
    function currencySymbol(code) { if (!code) return 'S/'; const c = String(code).toUpperCase(); if (c === 'PEN' || c === 'PEN-S' || c === 'PESO') return 'S/'; if (c === 'USD' || c === 'US' || c === 'DOLAR' || c === 'USD$') return '$'; return c + ' '; }
    function formatAmount(amount) { try { return new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount); } catch (e) { return Number(amount).toFixed(2); } }

    const priceInfo = resolvePrice(p);
    const priceBadge = document.createElement("div");
    priceBadge.className = "position-absolute top-0 end-0 m-2 badge rounded-pill";
    if (priceInfo && priceInfo.amount != null) {
      priceBadge.classList.add( "text-white");
      priceBadge.style.fontSize = "0.95rem";
      priceBadge.textContent = `${currencySymbol(priceInfo.currency)}${formatAmount(priceInfo.amount)}`;
    } else {
      priceBadge.classList.add("bg-secondary", "text-white");
      priceBadge.style.fontSize = "0.85rem";
      priceBadge.textContent = "Consultar precio";
    }

    const priceContainer = document.createElement("div");
    priceContainer.className = "card-price mb-2";
    const priceBox = document.createElement("div");
    priceBox.className = "mb-2 d-flex align-items-baseline gap-2";
    const priceMain = document.createElement("div");
    priceMain.className = "h5 fw-bold mb-0";
    if (priceInfo && priceInfo.amount != null) { priceMain.classList.add('text-success'); priceMain.textContent = `Desde ${currencySymbol(priceInfo.currency)}${formatAmount(priceInfo.amount)}`; } else { priceMain.textContent = 'Precio a consultar'; }
    priceBox.appendChild(priceMain);
    priceContainer.appendChild(priceBox);

    const meta = document.createElement("div");
    const servicios = p.servicios || p.services || [];
    if (Array.isArray(servicios) && servicios.length) {
      const snippet = servicios.slice(0, 2).map(s => s.nombre || s.name || String(s)).join(', ');
      meta.textContent = `Incluye: ${snippet}` + (servicios.length > 2 ? ` +${servicios.length - 2} más` : '');
    } else {
      meta.textContent = "Servicios no detallados.";
    }

    const footer = document.createElement('div');
    footer.className = 'mt-3 mt-auto d-flex justify-content-between align-items-center small gap-2 card-footer-cta';
    const codeBadge = document.createElement('span'); codeBadge.className = 'badge text-bg-primary ms-auto'; codeBadge.textContent = p.codigo || p.code || p.id || `PK-${idx + 1}`;
    const cta = document.createElement('div'); cta.className = 'd-flex gap-2 align-items-center';
    const verBtn = document.createElement('button'); verBtn.className = 'btn btn-sm btn-outline-secondary'; verBtn.textContent = 'Ver detalle'; verBtn.addEventListener('click', (ev) => { ev.preventDefault(); showPaqueteDetalle(p); });
    const btn = document.createElement('button'); btn.className = 'btn btn-sm btn-primary'; btn.textContent = 'Reservar / Contratar'; btn.addEventListener('click', () => solicitarContratacionDesdeCatalogo(p));
    cta.appendChild(verBtn); cta.appendChild(btn);

    body.appendChild(title); body.appendChild(desc); body.appendChild(priceContainer); body.appendChild(meta); footer.appendChild(codeBadge); footer.appendChild(cta); body.appendChild(footer);
    card.appendChild(body); card.appendChild(priceBadge); col.appendChild(card); fragment.appendChild(col);
  });
  cardsRow.appendChild(fragment);

  if (carouselInner && carouselWrap) {
    list.forEach((p, idx) => {
      const item = document.createElement('div');
      item.className = 'carousel-item' + (idx === 0 ? ' active' : '');
      const inner = document.createElement('div');
      inner.className = 'd-flex flex-column flex-md-row align-items-stretch p-4 bg-white border rounded-3 shadow-sm gap-3';
      inner.style.minHeight = '160px';
      const left = document.createElement('div'); left.className = 'flex-grow-1';
      const title = document.createElement('h5'); title.className = 'mb-1'; title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;
      const desc = document.createElement('p'); desc.className = 'mb-2 small text-muted'; desc.textContent = p.descripcion || p.description || 'Sin descripción.';
      const meta = document.createElement('div'); meta.className = 'small text-secondary'; const servicios = p.servicios || p.services || []; if (Array.isArray(servicios) && servicios.length) { meta.textContent = `Incluye ${servicios.length} servicio(s).`; } else { meta.textContent = 'Servicios no detallados.'; }
      left.appendChild(title); left.appendChild(desc); left.appendChild(meta);
      const right = document.createElement('div'); right.className = 'd-flex flex-column justify-content-end align-items-end';
      const cta = document.createElement('button'); cta.className = 'btn btn-sm btn-outline-primary'; cta.textContent = 'Contratar ahora'; cta.addEventListener('click', () => solicitarContratacionDesdeCatalogo(p)); right.appendChild(cta);
      inner.appendChild(left); inner.appendChild(right); item.appendChild(inner); carouselInner.appendChild(item);
    });
    if (list.length > 1) {
      carouselWrap.classList.remove('d-none');
    } else {
      carouselWrap.classList.add('d-none');
    }
  }
}
let loadingCatalogoMeta = false;

// =============================
//     META CATÁLOGO (abajo!!!!!
// =============================
async function loadCatalogoMeta() {
  const tiposListEl     = document.getElementById("catalogo-tipos-list");
  const serviciosListEl = document.getElementById("catalogo-servicios-list");

  // si no existen esos elementos, no hacemos nada
  if (!tiposListEl && !serviciosListEl) return;

  // 🔴 si ya se está ejecutando, no vuelvas a entrar
  if (loadingCatalogoMeta) return;
  loadingCatalogoMeta = true;

  try {
    // limpiamos SIEMPRE antes de pintar
    if (tiposListEl) tiposListEl.innerHTML = "";
    if (serviciosListEl) serviciosListEl.innerHTML = "";

    // 1) Traer tipos y servicios
    const [tipos, servicios] = await Promise.all([
      CATALOGO.tipos(),       // GET /v1/catalogo/tipos
      CATALOGO.servicios(),   // GET /v1/catalogo/servicios
    ]);

  const tiposList      = Array.isArray(tipos)     ? tipos     : (tipos?.items ?? []);
  const serviciosList  = Array.isArray(servicios) ? servicios : (servicios?.items ?? []);

  // expose meta for filters to use
  window.__catalogMetaTipos = tiposList;
  window.__catalogMetaServicios = serviciosList;

    // ---------- TIPOS ----------
    if (tiposListEl) {
      if (!tiposList.length) {
        const li = document.createElement("li");
        li.textContent = "No hay tipos de evento configurados.";
        tiposListEl.appendChild(li);
      } else {
        tiposList.forEach((t) => {
          const li = document.createElement("li");
          li.className = "mb-1";
          li.innerHTML =
            `<strong>${t.nombre}</strong><br>` +
            `<span class="text-muted">${t.descripcion || ""}</span>`;
          tiposListEl.appendChild(li);
        });
      }
    }

    // ---------- SERVICIOS POR TIPO ----------
    if (serviciosListEl) {
      if (!serviciosList.length) {
        serviciosListEl.textContent = "No hay servicios configurados.";
      } else {
        const byTipo = {};
        serviciosList.forEach((s) => {
          const tid = s.tipo_evento_id || s.tipo_id || "otros";
          (byTipo[tid] ||= []).push(s);
        });

        tiposList.forEach((t) => {
          const servs = byTipo[t.id] || [];
          if (!servs.length) return;

          const wrapper = document.createElement("div");
          wrapper.className = "mb-3";

          const title = document.createElement("div");
          title.className = "fw-semibold mb-1";
          title.textContent = t.nombre;
          wrapper.appendChild(title);

          const chips = document.createElement("div");
          chips.className = "d-flex flex-wrap gap-1";

          const vistos = new Set();
          servs.forEach((s) => {
            const name = s.nombre || s.name;
            if (!name || vistos.has(name)) return;
            vistos.add(name);

            const span = document.createElement("span");
            span.className = "badge rounded-pill bg-light text-dark border";
            span.textContent = name;
            chips.appendChild(span);
          });

          wrapper.appendChild(chips);
          serviciosListEl.appendChild(wrapper);
        });
      }
    }
  } catch (err) {
    console.error("Error cargando meta del catálogo", err);
    if (tiposListEl) tiposListEl.textContent       = "Error cargando tipos.";
    if (serviciosListEl) serviciosListEl.textContent = "Error cargando servicios.";
  } finally {
    // liberar la bandera
    loadingCatalogoMeta = false;
  }
}



// Mostrar modal con detalle de paquete (usa detalle si es necesario)
async function showPaqueteDetalle(paqueteOrId) {
  try {
    let paquete = paqueteOrId;
    const id = paquete?.id ?? paquete?.codigo ?? paquete?.code ?? paqueteOrId;
    if (!paquete || !paquete.items) {
      paquete = await CATALOGO.paquetePorId(id);
    }

    const precio = (() => {
      const pi = (paquete && (paquete.monto_total || paquete.monto)) ? { amount: paquete.monto_total ?? paquete.monto, currency: paquete.moneda ?? 'PEN' } : null;
      return pi;
    })();

    const itemsHtml = (paquete.items || []).map(it => {
      // Prefer human-friendly fields when available
      const nombre = it.nombre || it.servicio_nombre || it.opcion_nombre || it.nombre_opcion || it.descripcion || it.detalles || it.detalle || it.descripcion_servicio || it.servicio_desc || null;
      const title = nombre || (it.opcion_servicio_id || it.servicio_id || '-');
      const precioUnit = it.precio_unit_vigente || it.precio_unitario || it.precio || it.monto || null;
      const moneda = it.moneda || paquete.moneda || '';

      // Proveedores (si el backend devolvió proveedores por item)
      // Mostramos solo el proveedor "principal" (mejor nivel/rating) y un toggle para ver todos
      let provHtml = '';
      try {
        const provs = Array.isArray(it.proveedores) ? it.proveedores.slice() : [];
        // Deduplicar por id
        const seen = new Set();
        const uniq = [];
        for (const p of provs) {
          const id = String(p.proveedor_id || p.id || p.proveedor || '').trim();
          if (!id) continue;
          if (seen.has(id)) continue;
          seen.add(id);
          uniq.push(p);
        }

        if (uniq.length === 0) {
          provHtml = '<div class="small text-muted">-</div>';
        } else {
          // ordenar por nivel desc, luego rating desc
          uniq.sort((a,b) => {
            const na = Number(a.nivel || 0);
            const nb = Number(b.nivel || 0);
            if (nb !== na) return nb - na;
            const ra = Number(a.rating_prom || a.rating || 0);
            const rb = Number(b.rating_prom || b.rating || 0);
            return rb - ra;
          });

          const primary = uniq[0];
          const pname = escapeHtml(primary.proveedor_nombre || primary.nombre || primary.name || primary.proveedor_id || 'Proveedor');
          const pnivel = primary.nivel ? `<span class="badge bg-secondary ms-1">nivel ${escapeHtml(primary.nivel)}</span>` : '';

          // Only show the primary provider name (sin correo ni teléfono). No toggle ni lista completa.
          provHtml = `<div><strong>${pname}</strong>${pnivel}</div>`;
        }
      } catch (e) {
        console.error('Error renderizando proveedores', e);
        provHtml = '<div class="small text-muted">-</div>';
      }

      return `
        <tr>
          <td>${escapeHtml(title)}</td>
          <td>${it.cantidad || 1}</td>
          <td>${precioUnit ? (currencySymbol(moneda) + formatAmount(Number(precioUnit), moneda)) : '-'}</td>
          <td>${provHtml}</td>
        </tr>
      `;
    }).join('');

    const modalHtml = `
      <div class="modal fade" id="paqueteDetailModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">${paquete.nombre || paquete.name || 'Detalle del paquete'}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <p class="text-muted small">${paquete.descripcion || paquete.description || ''}</p>
              <div class="mb-3">
                <strong>Precio:</strong> ${precio ? (currencySymbol(precio.currency) + formatAmount(precio.amount, precio.currency)) : 'Consultar precio'}
              </div>
              <h6>Servicios incluidos</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead><tr><th>Servicio / Opción</th><th>Cantidad</th><th>Precio unit.</th><th>Proveedores</th></tr></thead>
                  <tbody>
                    ${itemsHtml || '<tr><td colspan="4" class="text-muted">No hay items detallados.</td></tr>'}
                  </tbody>
                </table>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
              <button type="button" class="btn btn-primary" id="paquete-contratar">Reservar / Contratar</button>
            </div>
          </div>
        </div>
      </div>
    `;

    const existing = document.getElementById('paqueteDetailModal');
    if (existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modalEl = document.getElementById('paqueteDetailModal');
    const modal = new bootstrap.Modal(modalEl);
    modalEl.addEventListener('hidden.bs.modal', () => modalEl.remove());

    modal.show();

    document.getElementById('paquete-contratar').addEventListener('click', () => {
      modal.hide();
      solicitarContratacionDesdeCatalogo(paquete);
    });
  } catch (e) {
    console.error('Error mostrando detalle de paquete', e);
    alert('No se pudo cargar el detalle del paquete');
  }
}

// ====== PROVEEDORES ======
async function loadProveedores() {
  const form = document.getElementById("proveedores-search-form");
  const results = document.getElementById("proveedores-results");
  const err = document.getElementById("proveedores-error");
  if (!form || !results) return;
  err.textContent = "";
  results.innerHTML = "";

  // Ensure the submit handler is attached only once
  if (!form._bound) {
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      err.textContent = "";
      results.innerHTML = "";
      const fd = new FormData(form);
      const servicio_id = (fd.get("servicio_id") || "").toString().trim();
      const fecha = (fd.get("fecha") || "").toString().trim();
      const limit = Number(fd.get("limit") || 20) || 20;
      try {
        const data = await PROVEEDORES.buscarDisponibles(
          servicio_id || null,
          fecha || "",
          limit,
          0
        );
        const list = Array.isArray(data) ? data : data?.items ?? [];
        if (!list.length) {
          err.textContent = "No se encontraron proveedores/disponibilidades.";
          return;
        }
        const frag = document.createDocumentFragment();
        list.forEach((item) => {
          const a = document.createElement("div");
          a.className =
            "list-group-item d-flex justify-content-between align-items-start";
          const left = document.createElement("div");
          left.innerHTML = `<div class="fw-semibold">${
            item.nombre || item.name || item.proveedor || "Proveedor"
          }</div><div class="small text-muted">${
            item.descripcion || item.desc || ""
          }</div>`;
          const right = document.createElement("div");
          right.className = "ms-auto";
          // Botón "Reservar" eliminado - ahora las reservas se crean vía Contratación service
          // Las holds son endpoints internos, no accesibles desde frontend
          a.appendChild(left);
          a.appendChild(right);
          frag.appendChild(a);
        });
        results.appendChild(frag);
      } catch (e) {
        console.error("Error buscando proveedores", e);
        err.textContent = e.message || "Error al consultar proveedores";
      }
    });
    form._bound = true;
  }
}

document.getElementById("buscar-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const servicioId = fd.get("servicio_id");
  const fecha = fd.get("fecha");
  const limit = fd.get("limit");

  const err = document.getElementById("buscar-error");
  const grid = document.getElementById("proveedores-grid");
  const count = document.getElementById("resultados-count");

  err.textContent = "";
  grid.innerHTML = '<div class="col-12 text-center"><div class="spinner-border text-primary"></div></div>';

  try {
    const proveedores = await PROVEEDORES.buscarDisponibles(servicioId, fecha);

    grid.innerHTML = "";
    count.textContent = `${proveedores.length} resultados`;

    if (proveedores.length === 0) {
      grid.innerHTML = `
        <div class="col-12 text-center text-secondary py-5">
          <i class="bi bi-inbox display-1"></i>
          <p class="mt-3">No se encontraron proveedores disponibles</p>
        </div>
      `;
      return;
    }

    proveedores.forEach(p => {
      const rating = Number(p.rating_prom || 0).toFixed(1);
      const stars = Math.round(rating);
      const starsHtml = '★'.repeat(stars) + '☆'.repeat(5 - stars);

      const card = document.createElement("div");
      card.className = "col-md-6 col-lg-4";
      card.innerHTML = `
        <div class="card proveedor-card h-100 shadow-sm" data-id="${p.id}">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h6 class="card-title mb-0">${p.nombre || 'Sin nombre'}</h6>
              <span class="badge ${p.status == 1 ? 'bg-success' : 'bg-secondary'}">
                ${p.status == 1 ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <p class="card-text small text-secondary mb-2">
              <i class="bi bi-envelope me-1"></i>${p.email || '—'}<br>
              <i class="bi bi-telephone me-1"></i>${p.telefono || '—'}
            </p>
            <div class="rating-stars mb-3">
              ${starsHtml} <span class="text-secondary">(${rating})</span>
            </div>
            <button class="btn btn-primary btn-sm w-100 btn-reservar" data-proveedor='${JSON.stringify(p)}'>
              <i class="bi bi-calendar-plus me-1"></i>Reservar
            </button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });

      // Listeners para botones de reserva
    document.querySelectorAll(".btn-reservar").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const p = JSON.parse(btn.dataset.proveedor);
        abrirModalReserva(p);
      });
    });

  } catch (error) {
    err.textContent = "Error al buscar: " + error.message;
    grid.innerHTML = "";
  }
});

document.getElementById("crear-reserva-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);

  const generateCorrelationId = () => {
    const randomHex = Array.from(crypto.getRandomValues(new Uint8Array(8)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    return `corr-${randomHex}`;
  };

  // Helper to ensure ISO datetime format
  const ensureISODateTime = (datetimeStr) => {
    if (!datetimeStr) return null;
    // If it already has seconds, return as is
    if (datetimeStr.length === 19) return datetimeStr;
    // If it's missing seconds, add ":00"
    if (datetimeStr.length === 16) return datetimeStr + ":00";
    return datetimeStr;
  };

  const data = {
    proveedor_id: fd.get("proveedor_id"),
    opcion_servicio_id: fd.get("opcion_servicio_id"),
    inicio: ensureISODateTime(fd.get("inicio")),
    fin: ensureISODateTime(fd.get("fin")),
    ttl_min: parseInt(fd.get("ttl_min")) || 30,
    correlation_id: fd.get("correlation_id") || generateCorrelationId(),
  };

  const err = document.getElementById("crear-reserva-error");
  err.textContent = "";

  // ⚠️ FUNCIONALIDAD DESHABILITADA: Las reservas (holds) ahora son endpoints internos
  // Solo Contratación-service puede crear holds. El frontend crea pedidos vía CONTRATACION service.
  alert("Las reservas directas ya no están disponibles. Use el flujo de Contratación para crear pedidos.");
  return;

  /*
  try {
    const reserva = await PROVEEDORES.crearReserva(data);
    crearReservaModal?.hide();

    showNotification(`Reserva creada exitosamente!\nID: ${reserva.id}\nExpira: ${reserva.expira_en}`, 'success');

    //alert(`Reserva creada exitosamente!\nID: ${reserva.id}\nExpira: ${reserva.expira_en}`);

    // Limpiar formulario
    e.target.reset();

    // Si está en la vista de reservas, recargar
    if (!views.reservas.classList.contains("d-none")) {
      cargarReservas();
    }
  } catch (error) {
    err.textContent = "Error: " + error.message;
  }
  */
});

function abrirModalReserva(proveedor) {
  if (!Auth.token) {
    alert("Debes iniciar sesión para crear reservas");
    return;
  }

  proveedorSeleccionado = proveedor;

  document.getElementById("proveedor-nombre").textContent = proveedor.nombre || "Proveedor";
  document.getElementById("proveedor-email").textContent = proveedor.email || "";
  document.getElementById("reserva-proveedor-id").value = proveedor.id;

  if (!crearReservaModal) {
    crearReservaModal = new bootstrap.Modal(document.getElementById("crearReservaModal"));
  }
  crearReservaModal.show();
}


// ====== CONTRATACION (vista de pedidos) ======
// ====== CONTRATACION (vista de pedidos) ======
async function loadContratacion() {
  const role = userRole();
  const titleEl = document.getElementById("contratacion-title");
  const subtitleEl = document.getElementById("contratacion-subtitle");
  const adminPanel = document.getElementById("contratacion-admin-panel");
  const clientCard = document.getElementById("contratacion-client-list-card");
  const userStats = document.getElementById("contratacion-user-stats");

  // ❌ NO tenemos el endpoint para listar TODOS los pedidos
  const ADMIN_TODOS_PEDIDOS_EXISTE = false;

  if (role === "ADMIN") {
    // Configurar encabezado para ADMIN
    if (titleEl) titleEl.textContent = "Gestión de Pedidos - ADMIN";
    if (subtitleEl) subtitleEl.textContent = "Administra pedidos del sistema (modo demostración)";

    // Mostrar panel admin y ocultar elementos propios de cliente
    if (adminPanel) adminPanel.classList.remove("d-none");
    if (clientCard) clientCard.classList.add("d-none");
    if (userStats) userStats.classList.add("d-none");

    // Cargar panel admin en modo demostración
    await loadAdminPedidos();
  } else {
    // Configurar encabezado para CLIENTE
    if (titleEl) titleEl.textContent = "Mis Pedidos";
    if (subtitleEl) subtitleEl.textContent = "Revisa el estado y detalles de tus pedidos contratados.";

    // Mostrar lista cliente y ocultar panel admin
    if (adminPanel) adminPanel.classList.add("d-none");
    if (clientCard) clientCard.classList.remove("d-none");
    if (userStats) userStats.classList.remove("d-none");

    await refreshMisPedidos();
  }
}

// Wrapper neutro para usar en botones de refresco

async function refreshPedidos() {
  const role = userRole();
  
  if (role === "ADMIN") {
    await loadAdminPedidos(); // Usar el modo demo
  } else {
    await refreshMisPedidos();
  }
}
// Mis pedidos (vista cliente)
async function refreshMisPedidos() {
  const listWrap = document.getElementById("contratacion-mis-pedidos");
  const emptyState = document.getElementById("contratacion-empty");
  const errorEl = document.getElementById("contratacion-error");

  if (!listWrap) return;

  listWrap.innerHTML = "";
  if (errorEl) errorEl.classList.add("d-none");
  if (emptyState) emptyState.classList.add("d-none");

  try {
    // ✅ CLIENTE: solo sus pedidos
    const pedidos = await CONTRATACION.misPedidos();
    const arr = Array.isArray(pedidos) ? pedidos : pedidos?.items ?? [];

    if (!arr.length) {
      if (emptyState) emptyState.classList.remove("d-none");
      // Stats en cero
      updateContratacionStats([], false);
      return;
    }

    // Ordenar por fecha más reciente primero
    arr.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    const frag = document.createDocumentFragment();

    arr.forEach((p) => {
      const pedidoItem = createPedidoItem(p, false);
      frag.appendChild(pedidoItem);
    });

    listWrap.appendChild(frag);

    // Actualizar estadísticas para cliente
    updateContratacionStats(arr, false);

  } catch (e) {
    console.error("Error cargando mis pedidos", e);
    if (errorEl) {
      errorEl.textContent = "Error al cargar pedidos: " + (e.message || "Intenta más tarde");
      errorEl.classList.remove("d-none");
    }
  }
}


function getStatusInfo(status) {
  const statusMap = {
    0: { text: '📝 Borrador', class: 'bg-secondary' },
    1: { text: '💰 Cotizado', class: 'bg-info' },
    2: { text: '✅ Aprobado', class: 'bg-success' },
    3: { text: '👥 Asignado', class: 'bg-primary' },
    4: { text: '🏁 Cerrado', class: 'bg-dark' },
    5: { text: '❌ Cancelado', class: 'bg-danger' }
  };
  return statusMap[status] || { text: 'Desconocido', class: 'bg-warning' };
}

function createPedidoItem(pedido, esAdmin = false) {
  // Para ADMIN utilizamos la tarjeta avanzada existente
  if (esAdmin) {
    return createAdminPedidoItem(pedido);
  }

  const item = document.createElement("div");
  item.className = "list-group-item list-group-item-action";

  const statusInfo = getStatusInfo(pedido.status);
  const fechaEvento = pedido.fecha_evento ? new Date(pedido.fecha_evento).toLocaleDateString('es-ES') : 'Por definir';
  const montoTotal = pedido.monto_total ? `S/ ${parseFloat(pedido.monto_total).toFixed(2)}` : 'Por cotizar';
  const createdDate = new Date(pedido.created_at).toLocaleDateString('es-ES');

  item.innerHTML = `
    <div class="d-flex justify-content-between align-items-start">
      <div class="flex-grow-1">
        <div class="d-flex align-items-center mb-2">
          <span class="badge ${statusInfo.class} me-2">${statusInfo.text}</span>
          <small class="text-muted">${pedido.pedido_id || pedido.id}</small>
        </div>

        <div class="mb-2">
          <strong>Evento:</strong> ${fechaEvento}
          ${pedido.hora_inicio ? ` - ${pedido.hora_inicio}` : ''}
        </div>

        <div class="mb-2">
          <strong>Ubicación:</strong> ${pedido.ubicacion || 'Por definir'}
        </div>

        <div class="mb-1">
          <strong>Monto:</strong> ${montoTotal}
        </div>

        <small class="text-muted">Creado: ${createdDate}</small>
      </div>

      <div class="text-end ms-3">
        <button class="btn btn-outline-primary btn-sm ver-detalle" data-pedido-id="${pedido.pedido_id || pedido.id}">
          <i class="bi bi-eye"></i> Detalle
        </button>
      </div>
    </div>
  `;

  // Agregar evento para ver detalle
  const detalleBtn = item.querySelector('.ver-detalle');
  detalleBtn.addEventListener('click', () => {
    verDetallePedido(pedido.id);
  });

  return item;
}

// Estadísticas unificadas (cliente = personales, admin = globales)
function updateContratacionStats(pedidos, esAdmin) {
  const stats = {
    total: pedidos.length,
    // Pendientes: borrador + cotizado
    pendientes: pedidos.filter(p => p.status === 0 || p.status === 1).length,
    // Confirmados: aprobado + asignado + cerrado
    confirmados: pedidos.filter(p => p.status === 2 || p.status === 3 || p.status === 4).length,
    cancelados: pedidos.filter(p => p.status === 5).length,
  };

  const totalEl = document.getElementById('stats-total');
  const pendEl = document.getElementById('stats-pendientes');
  const confEl = document.getElementById('stats-confirmados');
  const cancEl = document.getElementById('stats-cancelados');

  if (totalEl) totalEl.textContent = stats.total;
  if (pendEl) pendEl.textContent = stats.pendientes;
  if (confEl) confEl.textContent = stats.confirmados;
  if (cancEl) cancEl.textContent = stats.cancelados;

  // Para ADMIN también actualizamos el panel avanzado reutilizando la función existente
  if (esAdmin) {
    updateAdminPedidosStats(pedidos);
  }
}

async function verDetallePedido(pedidoId) {
  try {
    // Usa el endpoint existente de detalle
    const pedido = await CONTRATACION.detallePedido(pedidoId);

    const statusInfo = getStatusInfo(pedido.status);
    const fechaEvento = pedido.fecha_evento
      ? new Date(pedido.fecha_evento).toLocaleDateString("es-ES")
      : "Por definir";
    const montoTotal = pedido.monto_total
      ? `S/ ${parseFloat(pedido.monto_total || 0).toFixed(2)}`
      : "Por cotizar";

    alert(
      `Detalle del pedido ${pedido.pedido_id || pedido.id}` +
      `\nEstado: ${statusInfo.text}` +
      `\nFecha evento: ${fechaEvento}` +
      (pedido.hora_inicio ? ` ${pedido.hora_inicio}` : "") +
      `\nUbicación: ${pedido.ubicacion || "Por definir"}` +
      `\nTotal: ${montoTotal}`
    );
  } catch (error) {
    console.error("Error cargando detalle del pedido:", error);
    alert("No se pudo cargar el detalle del pedido");
  }
}

// ====== ADMIN GESTIÓN DE PEDIDOS ======
// ====== ADMIN GESTIÓN DE PEDIDOS ======
async function loadAdminPedidos() {
  try {
    await refreshAdminPedidos(); // ✅ Debe llamar a refreshAdminPedidos, NO a loadAdminPedidosDemo
  } catch (error) {
    console.error("❌ Error cargando pedidos ADMIN:", error);
    
    const listWrap = document.getElementById("admin-pedidos-list");
    const errorEl = document.getElementById("admin-pedidos-error");
    
    if (listWrap) {
      listWrap.innerHTML = `
        <div class="text-center py-5">
          <div class="alert alert-warning">
            <h6>⚠️ Error cargando pedidos</h6>
            <p class="mb-2">No se pudieron cargar los pedidos del sistema.</p>
            <small class="text-muted">Error: ${error.message || "Servicio no disponible"}</small>
          </div>
        </div>
      `;
    }
    
    if (errorEl) {
      errorEl.textContent = "No se pueden cargar los pedidos del sistema";
      errorEl.classList.remove("d-none");
    }
    
    updateAdminPedidosStats([]);
  }
}

async function refreshAdminPedidos() {
  const listWrap = document.getElementById("admin-pedidos-list");
  const emptyState = document.getElementById("admin-pedidos-empty");
  const errorEl = document.getElementById("admin-pedidos-error");

  if (!listWrap) return;

  listWrap.innerHTML = "";
  if (errorEl) errorEl.classList.add("d-none");
  if (emptyState) emptyState.classList.add("d-none");

  try {
    // Mostrar estado de carga
    listWrap.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div><p class="mt-2 text-muted">Cargando pedidos del sistema...</p></div>';
    
    console.log("🔄 Cargando pedidos para ADMIN...");
    
    // ✅ AHORA SÍ tenemos el endpoint completo
    const pedidos = await CONTRATACION.adminTodosPedidos();
    console.log("✅ Pedidos ADMIN cargados:", pedidos);
    
    const arr = Array.isArray(pedidos) ? pedidos : pedidos?.items ?? [];

    if (!arr.length) {
      listWrap.innerHTML = "";
      if (emptyState) emptyState.classList.remove("d-none");
      updateAdminPedidosStats([]);
      return;
    }

    // Aplicar filtros
    const statusFilterEl = document.getElementById("admin-filter-status");
    const searchIdEl = document.getElementById("admin-search-id");
    const searchClienteEl = document.getElementById("admin-search-cliente");

    const statusFilter = statusFilterEl ? statusFilterEl.value : "";
    const searchId = searchIdEl ? searchIdEl.value.trim().toLowerCase() : "";
    const searchCliente = searchClienteEl ? searchClienteEl.value.trim().toLowerCase() : "";

    let filtered = arr;

    if (statusFilter !== "") {
      const statusVal = parseInt(statusFilter);
      filtered = filtered.filter(p => p.status === statusVal);
    }

    if (searchId) {
      filtered = filtered.filter(p => String(p.id).toLowerCase().includes(searchId));
    }

    if (searchCliente) {
      filtered = filtered.filter(p => {
        const email = (p.cliente_email || p.email || "").toLowerCase();
        const nombre = (p.cliente_nombre || "").toLowerCase();
        return email.includes(searchCliente) || nombre.includes(searchCliente);
      });
    }

    listWrap.innerHTML = "";

    if (!filtered.length) {
      if (emptyState) emptyState.classList.remove("d-none");
    } else {
      // Ordenar por fecha más reciente primero
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      const frag = document.createDocumentFragment();

      // ✅ SOLO los pedidos, sin mensaje de demostración
      filtered.forEach((p) => {
        const pedidoItem = createAdminPedidoItem(p);
        frag.appendChild(pedidoItem);
      });

      listWrap.appendChild(frag);
    }

    // Actualizar estadísticas
    updateAdminPedidosStats(arr);

  } catch (e) {
    console.error("❌ Error en refreshAdminPedidos:", e);
    listWrap.innerHTML = "";
    
    if (errorEl) {
      errorEl.textContent = "Error al cargar pedidos: " + (e.message || "Intenta más tarde");
      errorEl.classList.remove("d-none");
    }
    
    throw e;
  }
}

function createAdminPedidoItem(pedido) {
  const item = document.createElement("div");
  item.className = "list-group-item list-group-item-action";
  
  const statusInfo = getStatusInfo(pedido.status);
  const fechaEvento = pedido.fecha_evento ? new Date(pedido.fecha_evento).toLocaleDateString('es-ES') : 'Por definir';
  const montoTotal = pedido.monto_total ? `S/ ${parseFloat(pedido.monto_total).toFixed(2)}` : 'Por cotizar';
  const createdDate = new Date(pedido.created_at).toLocaleDateString('es-ES');
  const clienteEmail = pedido.cliente_email || pedido.email || 'N/A';

  item.innerHTML = `
    <div class="d-flex justify-content-between align-items-start">
      <div class="flex-grow-1">
        <div class="d-flex align-items-center mb-2">
          <span class="badge ${statusInfo.class} me-2">${statusInfo.text}</span>
          <small class="text-muted">ID: ${pedido.pedido_id || pedido.id}</small>
          ${pedido.user_id ? `<small class="text-muted ms-2">User: ${pedido.user_id}</small>` : ''}
        </div>
        
        <div class="mb-2">
          <strong>Cliente:</strong> ${clienteEmail}
        </div>
        
        <div class="mb-2">
          <strong>Evento:</strong> ${fechaEvento}
          ${pedido.hora_inicio ? ` - ${pedido.hora_inicio}` : ''}
        </div>
        
        <div class="mb-2">
          <strong>Ubicación:</strong> ${pedido.ubicacion || 'Por definir'}
        </div>
        
        <div class="mb-2">
          <strong>Total:</strong> ${montoTotal}
        </div>
        
        <small class="text-muted">Creado: ${createdDate}</small>
        
        <!-- Dropdown para cambiar estado -->
        <div class="mt-3">
          <label class="form-label small mb-1">Cambiar Estado:</label>
          <select class="form-select form-select-sm estado-selector" data-pedido-id="${pedido.pedido_id || pedido.id}" style="max-width: 200px;">
            <option value="0" ${pedido.status == 0 ? 'selected' : ''}>📝 Borrador</option>
            <option value="1" ${pedido.status == 1 ? 'selected' : ''}>💰 Cotizado</option>
            <option value="2" ${pedido.status == 2 ? 'selected' : ''}>✅ Aprobado</option>
            <option value="3" ${pedido.status == 3 ? 'selected' : ''}>👥 Asignado</option>
            <option value="4" ${pedido.status == 4 ? 'selected' : ''}>🏁 Cerrado</option>
            <option value="5" ${pedido.status == 5 ? 'selected' : ''}>❌ Cancelado</option>
          </select>
        </div>
      </div>
      
      <div class="text-end ms-3 d-flex flex-column gap-2">
        <button class="btn btn-outline-primary btn-sm ver-detalle-admin" data-pedido-id="${pedido.pedido_id || pedido.id}">
          <i class="bi bi-eye"></i> Detalle
        </button>
        <button class="btn btn-outline-success btn-sm asignar-proveedor" data-pedido-id="${pedido.pedido_id || pedido.id}">
          <i class="bi bi-person-plus"></i> Asignar
        </button>
        <button class="btn btn-outline-info btn-sm agregar-items" data-pedido-id="${pedido.pedido_id || pedido.id}">
          <i class="bi bi-plus-circle"></i> Items
        </button>
      </div>
    </div>
  `;

  // Agregar evento para cambiar estado
  const estadoSelector = item.querySelector('.estado-selector');
  estadoSelector.addEventListener('change', (e) => {
    const nuevoEstado = parseInt(e.target.value);
    const estadoActual = pedido.status;
    const pedidoId = e.target.dataset.pedidoId;
    
    // Validar transición
    if (!esTransicionValida(estadoActual, nuevoEstado)) {
      showNotification(
        `Transición no permitida: ${getNombreEstado(estadoActual)} → ${getNombreEstado(nuevoEstado)}`,
        'error'
      );
      // Revertir el selector al estado actual
      e.target.value = estadoActual;
      return;
    }
    
    cambiarEstadoPedidoAdmin(pedidoId, nuevoEstado);
  });

  // Agregar eventos para los botones de acción
  const detalleBtn = item.querySelector('.ver-detalle-admin');
  detalleBtn.addEventListener('click', () => {
    verDetallePedidoAdmin(pedido.id);
  });

  const asignarBtn = item.querySelector('.asignar-proveedor');
  asignarBtn.addEventListener('click', () => {
    abrirModalAsignarProveedor(pedido.pedido_id || pedido.id);
  });

  const itemsBtn = item.querySelector('.agregar-items');
  itemsBtn.addEventListener('click', () => {
    abrirModalGestionItems(pedido.pedido_id || pedido.id);
  });

  return item;
}

async function cambiarEstadoPedidoAdmin(pedidoId, nuevoEstado) {
  try {
    console.log(`Cambiando estado del pedido ${pedidoId} a ${nuevoEstado}`);
    
    const body = { status: nuevoEstado };
    const resultado = await CONTRATACION.adminCambiarEstado(pedidoId, body);
    
    console.log("Estado cambiado exitosamente:", resultado);
    
    showNotification(`Estado del pedido ${pedidoId} actualizado correctamente`, 'success');
    
    setTimeout(() => {
      refreshAdminPedidos();
    }, 1000);
    
  } catch (error) {
    console.error('Error al cambiar estado del pedido:', error);
    showNotification(`Error al cambiar estado: ${error.message || 'Error desconocido'}`, 'error');
    
    refreshAdminPedidos();
  }
}

async function verDetallePedidoAdmin(pedidoId) {
  try {
    const pedido = await CONTRATACION.adminDetallePedido(pedidoId);
    
    const modalHtml = `
      <div class="modal fade" id="detallePedidoAdminModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header bg-primary text-white">
              <h5 class="modal-title">Detalle del Pedido - ADMIN</h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>Información Principal</h6>
                  <table class="table table-sm">
                    <tr><td><strong>ID:</strong></td><td>${pedido.pedido_id || pedido.id}</td></tr>
                    <tr><td><strong>Cliente:</strong></td><td>${pedido.cliente_email || pedido.email || 'N/A'}</td></tr>
                    <tr><td><strong>Estado:</strong></td><td><span class="badge ${getStatusInfo(pedido.status).class}">${getStatusInfo(pedido.status).text}</span></td></tr>
                    <tr><td><strong>Fecha Evento:</strong></td><td>${pedido.fecha_evento ? new Date(pedido.fecha_evento).toLocaleDateString('es-ES') : 'N/A'}</td></tr>
                    <tr><td><strong>Hora Inicio:</strong></td><td>${pedido.hora_inicio || 'N/A'}</td></tr>
                    <tr><td><strong>Ubicación:</strong></td><td>${pedido.ubicacion || 'N/A'}</td></tr>
                  </table>
                </div>
                <div class="col-md-6">
                  <h6>Información Económica</h6>
                  <table class="table table-sm">
                    <tr><td><strong>Monto Total:</strong></td><td>${pedido.monto_total ? `S/ ${parseFloat(pedido.monto_total).toFixed(2)}` : 'Por cotizar'}</td></tr>
                    <tr><td><strong>Fecha Creación:</strong></td><td>${new Date(pedido.created_at).toLocaleString('es-ES')}</td></tr>
                    <tr><td><strong>Última Actualización:</strong></td><td>${pedido.updated_at ? new Date(pedido.updated_at).toLocaleString('es-ES') : 'N/A'}</td></tr>
                  </table>
                </div>
              </div>
              
              ${pedido.items && pedido.items.length > 0 ? `
                <div class="mt-4">
                  <h6>Items del Pedido</h6>
                  <div class="table-responsive">
                    <table class="table table-sm table-striped">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Servicio / Opción</th>
                          <th>Cant.</th>
                          <th>Precio Unit.</th>
                          <th>Subtotal</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${pedido.items.map(item => `
                          <tr>
                            <td><code class="small">${item.id ? item.id.substring(0, 8) + '...' : '-'}</code></td>
                            <td>
                              <strong>${item.nombre_servicio || item.servicio_nombre || item.opcion_nombre || 'Servicio'}</strong><br>
                              ${item.opcion_servicio_id ? `<small class="text-muted">Opción: ${item.opcion_servicio_id.substring(0, 12)}...</small>` : ''}
                            </td>
                            <td>${item.cantidad || 1}</td>
                            <td>${item.precio_unitario ? `S/ ${parseFloat(item.precio_unitario).toFixed(2)}` : 'N/A'}</td>
                            <td class="fw-semibold">${item.subtotal ? `S/ ${parseFloat(item.subtotal).toFixed(2)}` : 'N/A'}</td>
                          </tr>
                        `).join('')}
                      </tbody>
                      <tfoot>
                        <tr class="table-primary">
                          <td colspan="4" class="text-end"><strong>Total:</strong></td>
                          <td class="fw-bold">${pedido.monto_total ? `S/ ${parseFloat(pedido.monto_total).toFixed(2)}` : 'Por calcular'}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              ` : '<p class="text-muted">No hay items registrados en este pedido.</p>'}
              
              ${pedido.proveedores && pedido.proveedores.length > 0 ? `
                <div class="mt-4">
                  <h6>Proveedores involucrados</h6>
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr><th>Proveedor</th><th>Email</th><th>Acción</th></tr>
                      </thead>
                      <tbody>
                        ${pedido.proveedores.map(pr => `
                          <tr>
                            <td>${pr.nombre || pr.name || pr.id}</td>
                            <td>${pr.email || '-'}</td>
                            <td><button class="btn btn-sm btn-outline-primary ver-proveedor" data-prov-id="${pr.id}">Ver</button></td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                  </div>
                </div>
              ` : ''}
              
              <div class="mt-4">
                <h6>Acciones Administrativas</h6>
                <div class="d-flex gap-2 flex-wrap">
                  <select class="form-select form-select-sm" style="width: auto;" id="modal-estado-selector">
                    <option value="0" ${pedido.status == 0 ? 'selected' : ''}>📝 Borrador</option>
                    <option value="1" ${pedido.status == 1 ? 'selected' : ''}>💰 Cotizado</option>
                    <option value="2" ${pedido.status == 2 ? 'selected' : ''}>✅ Aprobado</option>
                    <option value="3" ${pedido.status == 3 ? 'selected' : ''}>👥 Asignado</option>
                    <option value="4" ${pedido.status == 4 ? 'selected' : ''}>🏁 Cerrado</option>
                    <option value="5" ${pedido.status == 5 ? 'selected' : ''}>❌ Cancelado</option>
                  </select>
                  <button class="btn btn-primary btn-sm" id="modal-cambiar-estado">Aplicar Estado</button>
                  <button class="btn btn-success btn-sm" id="modal-asignar-proveedor">Asignar Proveedor</button>
                  <button class="btn btn-info btn-sm" id="modal-agregar-items">Gestionar Items</button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Remover modal existente si hay
    const existingModal = document.getElementById('detallePedidoAdminModal');
    if (existingModal) {
      existingModal.remove();
    }

    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modalElement = document.getElementById('detallePedidoAdminModal');
    const modal = new bootstrap.Modal(modalElement);

    // Configurar eventos del modal
    document.getElementById('modal-cambiar-estado').addEventListener('click', () => {
      const nuevoEstado = parseInt(document.getElementById('modal-estado-selector').value);
      const estadoActual = pedido.status;
      
      // Validar transición
      if (!esTransicionValida(estadoActual, nuevoEstado)) {
        showNotification(
          `Transición no permitida: ${getNombreEstado(estadoActual)} → ${getNombreEstado(nuevoEstado)}`,
          'error'
        );
        return;
      }
      
      cambiarEstadoPedidoAdmin(pedidoId, nuevoEstado);
      modal.hide();
    });

    document.getElementById('modal-asignar-proveedor').addEventListener('click', () => {
      modal.hide();
      setTimeout(() => abrirModalAsignarProveedor(pedidoId), 300);
    });

    document.getElementById('modal-agregar-items').addEventListener('click', () => {
      modal.hide();
      setTimeout(() => abrirModalGestionItems(pedidoId), 300);
    });

    modal.show();
    
    // Limpiar modal cuando se cierre
    modalElement.addEventListener('hidden.bs.modal', () => {
      modalElement.remove();
    });

    // Handler para botones "Ver proveedor" (muestra info básica incluida en la respuesta)
    modalElement.querySelectorAll('.ver-proveedor').forEach(btn => {
      btn.addEventListener('click', (ev) => {
        const pid = btn.dataset.provId;
        const prov = (pedido.proveedores || []).find(x => String(x.id) === String(pid));
        if (prov) {
          alert(`Proveedor: ${prov.nombre || prov.id}\nEmail: ${prov.email || 'N/A'}`);
        } else {
          alert('Proveedor no encontrado');
        }
      });
    });

  } catch (error) {
    console.error('Error cargando detalle del pedido admin:', error);
    showNotification('No se pudo cargar el detalle del pedido', 'error');
  }
}

function updateAdminPedidosStats(pedidos) {
  const stats = {
    total: pedidos.length,
    cotizados: pedidos.filter(p => p.status === 1).length,
    aprobados: pedidos.filter(p => p.status === 2).length,
    asignados: pedidos.filter(p => p.status === 3).length,
    cerrados: pedidos.filter(p => p.status === 4).length,
    cancelados: pedidos.filter(p => p.status === 5).length
  };

  const totalEl = document.getElementById('admin-stats-total');
  const cotizadosEl = document.getElementById('admin-stats-cotizados');
  const aprobadosEl = document.getElementById('admin-stats-aprobados');
  const asignadosEl = document.getElementById('admin-stats-asignados');
  const cerradosEl = document.getElementById('admin-stats-cerrados');
  const canceladosEl = document.getElementById('admin-stats-cancelados');

  if (totalEl) totalEl.textContent = stats.total;
  if (cotizadosEl) cotizadosEl.textContent = stats.cotizados;
  if (aprobadosEl) aprobadosEl.textContent = stats.aprobados;
  if (asignadosEl) asignadosEl.textContent = stats.asignados;
  if (cerradosEl) cerradosEl.textContent = stats.cerrados;
  if (canceladosEl) canceladosEl.textContent = stats.cancelados;
}

function aplicarFiltrosAdmin() {
  refreshAdminPedidos();
}

// Función auxiliar para mostrar notificaciones
function showNotification(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container') || createToastContainer();
  
  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement);
  toast.show();
  
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove();
  });
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container position-fixed top-0 end-0 p-3';
  container.style.zIndex = '9999';
  document.body.appendChild(container);
  return container;
}

// ====== ADMIN LISTA USUARIOS ======
async function loadUsers() {
  const tbody = document.getElementById("users-tbody");
  const err = document.getElementById("admin-error");
  tbody.innerHTML = "";
  err.textContent = "";
  try {
    const emailFilterEl = document.getElementById("admin-filter-email");
    const emailFilter = emailFilterEl && String(emailFilterEl.value || "").trim();

    // Si hay un filtro por email, haremos una recolección paginada de resultados
    // para cubrir "todas las hojas" (todas las páginas). Esto asegura que
    // la búsqueda encuentre coincidencias en todo el dataset aunque el backend
    // no aplique filtros server-side. Hay un tope de seguridad para evitar loops.
    async function fetchAllUsersByEmail(email) {
      const perPage = 200; // chunk size
      const maxRecords = 5000; // safety cap
      let offsetLocal = 0;
      const all = [];
      while (all.length < maxRecords) {
        const dataChunk = await IAM.adminUsers(perPage, offsetLocal, email || undefined);
        const itemsChunk = (dataChunk && dataChunk.items) ? dataChunk.items : dataChunk;
        if (!itemsChunk || itemsChunk.length === 0) break;
        all.push(...itemsChunk);
        if (itemsChunk.length < perPage) break; // última página
        offsetLocal += perPage;
      }
      return all.slice(0, maxRecords);
    }

    let items;
    if (emailFilter) {
      // Mostrar indicador simple mientras buscamos
      err.textContent = "Buscando usuarios...";
      items = await fetchAllUsersByEmail(emailFilter);
      adminTotal = Array.isArray(items) ? items.length : null;
      adminOffset = 0; // resetear paginación
      err.textContent = "";
    } else {
      const data = await IAM.adminUsers(adminLimit, adminOffset);
      items = (data && data.items) ? data.items : data;
      adminTotal =
        data && (data.total || data.count || (data.meta && data.meta.total)) ||
        adminTotal;
    }

    // Fallback client-side: si el backend no aplicó el filtro, aplicar aquí
    let filteredItems = items;
    if (emailFilter && Array.isArray(items)) {
      const q = String(emailFilter).toLowerCase();
      filteredItems = items.filter(u => (u && u.email && String(u.email).toLowerCase().includes(q)));
    }

    console.log("[loadUsers] items received:", Array.isArray(items) ? items.length : items);

    let appended = 0;
    (filteredItems ?? []).forEach((u, idx) => {
      try {
        const tr = document.createElement("tr");
        const id = u.id ?? "";
        const email = u.email ?? "";
        const role = u.role ?? "";
        const status = Number(u.status) === 1 ? "Activo" : "Inactivo";

        tr.innerHTML = `
          <td>${id}</td>
          <td>${email}</td>
          <td>${role}</td>
          <td>${status}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary me-1 edit-user" data-id="${id}" title="Editar">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-user" data-id="${id}" title="Eliminar">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
        appended++;
      } catch (rowErr) {
        console.error("[loadUsers] error rendering row index", idx, rowErr);
        // show a lightweight debug row so the admin sees something
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="5" class="text-danger small">Error renderizando usuario en fila ${idx}</td>`;
        tbody.appendChild(tr);
      }
    });

    console.log("[loadUsers] rows appended:", appended);

    tbody.querySelectorAll(".edit-user").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.currentTarget.dataset.id;
        await openEditModal(id);
      });
    });

    tbody.querySelectorAll(".delete-user").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.currentTarget.dataset.id;
        confirmDeleteUser(id);
      });
    });
  } catch (e) {
    err.textContent = "No autorizado o error: " + e.message;
  }

  renderAdminPagination();
}

function renderAdminPagination() {
  const container = document.getElementById("admin-pagination");
  const info = document.getElementById("admin-pagination-info");
  if (!container || !info) return;

  container.innerHTML = "";

  const btnPrev = document.createElement("button");
  btnPrev.className = "btn btn-sm btn-outline-secondary";
  btnPrev.textContent = "« Prev";
  btnPrev.disabled = adminOffset <= 0;
  btnPrev.addEventListener("click", async () => {
    if (adminOffset <= 0) return;
    adminOffset = Math.max(0, adminOffset - adminLimit);
    await loadUsers();
  });

  const btnNext = document.createElement("button");
  btnNext.className = "btn btn-sm btn-outline-secondary";
  btnNext.textContent = "Next »";
  let disableNext = false;
  if (adminTotal !== null) {
    disableNext = adminOffset + adminLimit >= adminTotal;
  }
  btnNext.disabled = disableNext;
  btnNext.addEventListener("click", async () => {
    if (adminTotal !== null && adminOffset + adminLimit >= adminTotal) return;
    adminOffset = adminOffset + adminLimit;
    await loadUsers();
  });

  container.appendChild(btnPrev);
  container.appendChild(btnNext);

  const page = Math.floor(adminOffset / adminLimit) + 1;
  const from = adminOffset + 1;
  const to = adminOffset + adminLimit;
  if (adminTotal !== null) {
    info.textContent = `Página ${page} — mostrando ${from}-${Math.min(
      to,
      adminTotal
    )} de ${adminTotal}`;
  } else {
    info.textContent = `Página ${page} — items ${from}-${to}`;
  }
}

// Modal para editar usuario
let editUserModal = null;
function ensureEditModal() {
  if (!editUserModal) {
    const el = document.getElementById("editUserModal");
    if (el && window.bootstrap?.Modal)
      editUserModal = new bootstrap.Modal(el);
  }
}

async function openEditModal(id) {
  ensureEditModal();
  const form = document.getElementById("edit-user-form");
  const err = document.getElementById("edit-error");
  err.textContent = "";
  try {
    console.log('[openEditModal] loading user', id);
    const u = await IAM.adminGetUser(id);
    form["id"].value = u.id;
    form["nombre"].value = u.nombre || "";
    form["telefono"].value = u.telefono || "";
    form["role"].value = u.role || "CLIENTE";
    form["status"].value = String(u.status ?? 1);
    if (form["password"]) form["password"].value = "";
    // Ensure the submit button is enabled and shows default text (in case a previous save left it disabled)
    try {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Guardar cambios';
        submitBtn.classList.remove('btn-success');
      }
    } catch (btnErr) { console.warn('Could not reset submit button', btnErr); }

    editUserModal?.show();
    // focus first input when modal shown
    try {
      const modalEl = document.getElementById('editUserModal');
      modalEl?.addEventListener('shown.bs.modal', () => {
        const first = form.querySelector('input[name="nombre"]') || form.querySelector('input');
        try { first && first.focus(); } catch(e){}
      }, { once: true });
    } catch(e){}
  } catch (e) {
    alert("Error al cargar usuario: " + e.message);
  }
}

document.getElementById("edit-user-form")?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const id = fd.get("id");
    const err = document.getElementById("edit-error");
    err.textContent = "";

    const submitBtn = ev.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Guardando...";

    try {
        const patch = {
            nombre: (fd.get("nombre") || "").toString(),
            telefono: (fd.get("telefono") || "").toString(),
            status: Number(fd.get("status")),
            role: (fd.get("role") || "CLIENTE").toString(),
        };

        const password = (fd.get("password") || "").toString();
        
        // Solo incluir password en el patch si NO está vacío
        if (password.trim().length > 0) {
            if (password.length < 6) {
                throw new Error("La contraseña debe tener al menos 6 caracteres");
            }
            patch.password = password;
            console.log("🔄 Incluyendo nuevo password en la actualización");
        } else {
            console.log("🔒 Manteniendo password actual (campo vacío)");
        }

        console.log("🔄 Enviando actualización:", patch);
        await IAM.adminPatchUser(id, patch);
        
        // Éxito
        submitBtn.textContent = "✓ Guardado";
        submitBtn.classList.add("btn-success");
        
        setTimeout(() => {
            editUserModal?.hide();
            loadUsers();
        }, 1000);
        
    } catch (e) {
        console.error("❌ Error:", e);
        err.textContent = "Error: " + (e.message || "No se pudo actualizar el usuario");
        
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
        submitBtn.classList.remove("btn-success");
    }
});

// Confirmación para eliminar
async function confirmDeleteUser(id) {
  const ok = confirm("¿Seguro que deseas eliminar este usuario?");
  if (!ok) return;
  try {
    await IAM.adminDeleteUser(id);
    await loadUsers();
  } catch (e) {
    alert("No se pudo eliminar: " + e.message);
  }
}

// ====== MODALES ADMIN: ASIGNAR PROVEEDOR Y GESTIÓN DE ITEMS ======
let asignarProveedorModal = null;
let gestionItemsModal = null;

function setupAdminModals() {
  // Inicializar modales
  const asignarEl = document.getElementById('asignarProveedorModal');
  const gestionEl = document.getElementById('gestionItemsModal');
  
  if (asignarEl && window.bootstrap?.Modal) {
    asignarProveedorModal = new bootstrap.Modal(asignarEl);
  }
  
  if (gestionEl && window.bootstrap?.Modal) {
    gestionItemsModal = new bootstrap.Modal(gestionEl);
  }

  // Form: Asignar Proveedor
  const asignarForm = document.getElementById('asignar-proveedor-form');
  if (asignarForm && !asignarForm._bound) {
    asignarForm.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const pedidoId = fd.get('pedido_id');
      const proveedorId = fd.get('proveedor_id');
      const errorEl = document.getElementById('asignar-proveedor-error');
      errorEl.textContent = '';

      try {
        // Obtener items seleccionados (checkboxes)
        const itemCheckboxes = document.querySelectorAll('#asignar-items-list input[type="checkbox"]:checked');
        const itemIds = Array.from(itemCheckboxes).map(cb => cb.value);

        if (!itemIds.length) {
          errorEl.textContent = 'Debe seleccionar al menos un item';
          return;
        }

        const payload = {
          item_pedido_ids: itemIds,
          proveedor_id: proveedorId
        };

        console.log('Asignando proveedor:', payload);
        await CONTRATACION.adminAsignarProveedor(pedidoId, payload);
        
        showNotification(`Proveedor asignado exitosamente a ${itemIds.length} item(s)`, 'success');
        asignarProveedorModal?.hide();
        asignarForm.reset();
        
        // Recargar vista de pedidos
        setTimeout(() => refreshAdminPedidos(), 500);
      } catch (e) {
        console.error('Error asignando proveedor:', e);
        errorEl.textContent = e.message || 'Error al asignar proveedor';
      }
    });
    asignarForm._bound = true;
  }

  // Form: Agregar Items
  const agregarForm = document.getElementById('agregar-items-form');
  if (agregarForm && !agregarForm._bound) {
    agregarForm.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const pedidoId = fd.get('pedido_id_agregar');
      const errorEl = document.getElementById('agregar-items-error');
      errorEl.textContent = '';

      try {
        const payload = {
          items: [{
            opcion_servicio_id: fd.get('opcion_servicio_id'),
            cantidad: parseInt(fd.get('cantidad')) || 1,
            precio_unit_vigente: fd.get('precio_unit_vigente') ? parseFloat(fd.get('precio_unit_vigente')) : undefined,
            nombre_servicio: fd.get('nombre_servicio') || undefined
          }]
        };

        console.log('Agregando items:', payload);
        await CONTRATACION.adminAgregarItems(pedidoId, payload);
        
        showNotification('Items agregados exitosamente', 'success');
        agregarForm.reset();
        
        // Recargar lista de items para eliminar
        await cargarItemsParaEliminar(pedidoId);
        setTimeout(() => refreshAdminPedidos(), 500);
      } catch (e) {
        console.error('Error agregando items:', e);
        errorEl.textContent = e.message || 'Error al agregar items';
      }
    });
    agregarForm._bound = true;
  }

  // Form: Eliminar Items
  const eliminarForm = document.getElementById('eliminar-items-form');
  if (eliminarForm && !eliminarForm._bound) {
    eliminarForm.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const pedidoId = fd.get('pedido_id_eliminar');
      const itemIdsStr = fd.get('item_ids');
      const errorEl = document.getElementById('eliminar-items-error');
      errorEl.textContent = '';

      try {
        const itemIds = itemIdsStr.split(',').map(s => s.trim()).filter(Boolean);
        
        if (!itemIds.length) {
          errorEl.textContent = 'Ingrese al menos un ID de item';
          return;
        }

        const payload = { item_ids: itemIds };

        console.log('Eliminando items:', payload);
        await CONTRATACION.adminEliminarItems(pedidoId, payload);
        
        showNotification(`${itemIds.length} item(s) eliminado(s) exitosamente`, 'success');
        eliminarForm.reset();
        
        // Recargar lista
        await cargarItemsParaEliminar(pedidoId);
        setTimeout(() => refreshAdminPedidos(), 500);
      } catch (e) {
        console.error('Error eliminando items:', e);
        errorEl.textContent = e.message || 'Error al eliminar items';
      }
    });
    eliminarForm._bound = true;
  }
}

async function abrirModalAsignarProveedor(pedidoId) {
  try {
    const pedido = await CONTRATACION.adminDetallePedido(pedidoId);
    
    // Validar que el pedido esté en estado APROBADO (2)
    if (pedido.status !== 2) {
      showNotification('Solo se pueden asignar proveedores a pedidos APROBADOS', 'error');
      return;
    }

    // Actualizar info del modal
    document.getElementById('asignar-pedido-id').textContent = pedido.pedido_id || pedido.id;
    document.getElementById('asignar-pedido-estado').innerHTML = `<span class="badge ${getStatusInfo(pedido.status).class}">${getStatusInfo(pedido.status).text}</span>`;
    document.getElementById('asignar-hidden-pedido-id').value = pedido.pedido_id || pedido.id;

    // Cargar items con checkboxes
    const itemsList = document.getElementById('asignar-items-list');
    if (!pedido.items || !pedido.items.length) {
      itemsList.innerHTML = '<div class="text-muted small">No hay items en este pedido</div>';
    } else {
      itemsList.innerHTML = pedido.items.map(item => `
        <div class="form-check">
          <input class="form-check-input" type="checkbox" value="${item.id}" id="item-${item.id}">
          <label class="form-check-label small" for="item-${item.id}">
            ${item.nombre_servicio || item.opcion_servicio_id || 'Item'} 
            (${item.cantidad || 1} x ${item.precio_unitario ? 'S/ ' + parseFloat(item.precio_unitario).toFixed(2) : 'N/A'})
          </label>
        </div>
      `).join('');
    }

    asignarProveedorModal?.show();
  } catch (e) {
    console.error('Error abriendo modal asignar proveedor:', e);
    showNotification('Error al cargar datos del pedido', 'error');
  }
}

async function abrirModalGestionItems(pedidoId) {
  try {
    const pedido = await CONTRATACION.adminDetallePedido(pedidoId);
    
    document.getElementById('gestion-pedido-id').textContent = pedido.pedido_id || pedido.id;
    document.getElementById('gestion-hidden-pedido-id-agregar').value = pedido.pedido_id || pedido.id;
    document.getElementById('gestion-hidden-pedido-id-eliminar').value = pedido.pedido_id || pedido.id;

    await cargarItemsParaEliminar(pedido.pedido_id || pedido.id);

    gestionItemsModal?.show();
  } catch (e) {
    console.error('Error abriendo modal gestión items:', e);
    showNotification('Error al cargar datos del pedido', 'error');
  }
}

async function cargarItemsParaEliminar(pedidoId) {
  try {
    const pedido = await CONTRATACION.adminDetallePedido(pedidoId);
    const itemsList = document.getElementById('eliminar-items-list');
    
    if (!pedido.items || !pedido.items.length) {
      itemsList.innerHTML = '<div class="text-muted small">No hay items en este pedido</div>';
    } else {
      itemsList.innerHTML = pedido.items.map(item => `
        <div class="border-bottom pb-2 mb-2">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <strong class="small">${item.nombre_servicio || item.opcion_servicio_id || 'Item'}</strong><br>
              <code class="small">${item.id}</code>
            </div>
            <div class="text-end small">
              <div>Cant: ${item.cantidad || 1}</div>
              <div>${item.precio_unitario ? 'S/ ' + parseFloat(item.precio_unitario).toFixed(2) : 'N/A'}</div>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error cargando items:', e);
  }
}

// Validación de transiciones de estado permitidas
const TRANSICIONES_VALIDAS = {
  0: [1, 5], // DRAFT -> COTIZADO, CANCELADO
  1: [2, 5], // COTIZADO -> APROBADO, CANCELADO
  2: [3, 5], // APROBADO -> ASIGNADO, CANCELADO
  3: [4, 5], // ASIGNADO -> CERRADO, CANCELADO
  4: [],     // CERRADO (final)
  5: []      // CANCELADO (final)
};

function esTransicionValida(estadoActual, estadoNuevo) {
  const transiciones = TRANSICIONES_VALIDAS[estadoActual] || [];
  return transiciones.includes(estadoNuevo);
}

function getNombreEstado(estado) {
  const nombres = {
    0: 'BORRADOR',
    1: 'COTIZADO',
    2: 'APROBADO',
    3: 'ASIGNADO',
    4: 'CERRADO',
    5: 'CANCELADO'
  };
  return nombres[estado] || 'DESCONOCIDO';
}

// ====== LOGIN / LOGOUT ======
document
  .getElementById("login-form")
  ?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const email = (fd.get("email") || "").toString();
    const password = (fd.get("password") || "").toString();
    const err = document.getElementById("login-error");
    err.textContent = "";
    try {
      const u = await Auth.login(email, password);
      currentUser = u;
      navLogin?.classList.add("d-none");
      navLogout?.classList.remove("d-none");
      configureNavbar();

      // Si venías de catálogo con un paquete pendiente, se contrata aquí
      const executed = await runPendingContratacion();
      if (!executed) {
        location.hash = "/me";
      }
    } catch (e) {
      console.error(e);
      err.textContent = "Credenciales inválidas o error de servidor.";
    }
  });

navLogout?.addEventListener("click", (e) => {
  e.preventDefault();
  Auth.logout();
  currentUser = null;
  navLogout?.classList.add("d-none");
  navLogin?.classList.remove("d-none");
  configureNavbar();
  location.hash = "/";
});

// ----- ADMIN recargar -----
document
  .getElementById("btn-admin-reload")
  ?.addEventListener("click", (e) => {
    e.preventDefault();
    loadUsers();
  });

// ----- Abrir modal desde link en Login -----
openPublicRegister?.addEventListener("click", (e) => {
  e.preventDefault();
  ensurePublicModal();
  publicRegisterModal?.show();
});

// ======= NAVBAR SMART =======
function configureNavbar() {
  const isLogged = !!Auth.token;
  const role = userRole();

  navLogin?.classList.toggle("d-none", isLogged);
  navLogout?.classList.toggle("d-none", !isLogged);

  if (!isLogged) {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#");
    navRegister?.setAttribute("data-mode", "public");
    navAdmin?.classList.add("d-none");
    navProveedores?.classList.add("d-none");
  } else if (role === "ADMIN") {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#/admin-register");
    navRegister?.setAttribute("data-mode", "admin");
    navAdmin?.classList.remove("d-none");
    navProveedores?.classList.remove("d-none");  // Solo ADMIN ve Proveedores
  } else {
    navRegister?.classList.add("d-none");
    navRegister?.setAttribute("data-mode", "hidden");
    navAdmin?.classList.add("d-none");
    navProveedores?.classList.add("d-none");  // CLIENTE no ve Proveedores
  }
}

navRegister?.addEventListener("click", (e) => {
  const mode = navRegister.getAttribute("data-mode");
  if (mode === "public") {
    e.preventDefault();
    ensurePublicModal();
    publicRegisterModal?.show();
  }
});

// QuickLogin buttons (autofill + submit)
try {
  const qClient = document.getElementById('quicklogin-client');
  const qAdmin = document.getElementById('quicklogin-admin');
  const loginForm = document.getElementById('login-form');
  const emailInput = document.querySelector('#login-form input[name="email"]');
  const passInput = document.querySelector('#login-form input[name="password"]');

  if (qClient) qClient.addEventListener('click', (e) => {
    e.preventDefault();
    try {
      emailInput.value = window.QUICKLOGIN_CLIENT_EMAIL || '';
      passInput.value = window.QUICKLOGIN_CLIENT_PASSWORD || '';
      // submit
      loginForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    } catch (err) { console.error('QuickClient error', err); }
  });

  if (qAdmin) qAdmin.addEventListener('click', (e) => {
    e.preventDefault();
    try {
      const adminEmail = window.QUICKLOGIN_ADMIN_EMAIL || '';
      const adminPass = window.QUICKLOGIN_ADMIN_PASSWORD || '';
      if (!adminEmail || !adminPass) {
        const manual = confirm('No hay credenciales admin configuradas en config.js. ¿Deseas ingresar manualmente ahora?');
        if (!manual) return;
        const em = prompt('Admin email:','');
        const pw = prompt('Admin password:','');
        if (!em || !pw) return;
        emailInput.value = em;
        passInput.value = pw;
      } else {
        emailInput.value = adminEmail;
        passInput.value = adminPass;
      }
      loginForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    } catch (err) { console.error('QuickAdmin error', err); }
  });
} catch (e) { /* noop */ }

// ----- Registro PÚBLICO (modal) -----
document
  .getElementById("public-register-form")
  ?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const email = (fd.get("email") || "").toString();
    const password = (fd.get("password") || "").toString();
    const nombre = (fd.get("nombre") || "").toString();
    const telefono = (fd.get("telefono") || "").toString();
    const err = document.getElementById("public-register-error");
    err.textContent = "";
    try {
      await IAM.register(email, password, nombre, telefono);
      ensurePublicModal();
      publicRegisterModal?.hide();
      location.hash = "/login";
      setTimeout(() => {
        const emailInput = document.querySelector(
          '#login-form input[name="email"]'
        );
        if (emailInput) emailInput.value = email;
      }, 50);
    } catch (e) {
      err.textContent = "No se pudo registrar: " + e.message;
    }
  });

// ----- Registro ADMIN -----
document
  .getElementById("admin-create-form")
  ?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const payload = {
      email: (fd.get("email") || "").toString(),
      password: (fd.get("password") || "").toString(),
      nombre: (fd.get("nombre") || "").toString(),
      telefono: (fd.get("telefono") || "").toString(),
      role:
        (fd.get("role") || "").toString().toUpperCase() ||
        "CLIENTE",
    };
    const err = document.getElementById("admin-create-error");
    const ok = document.getElementById("admin-create-ok");
    err.textContent = "";
    ok?.classList.add("d-none");
    try {
      await IAM.adminCreateUser(payload);
      ok?.classList.remove("d-none");
      ev.target.reset();
    } catch (e) {
      err.textContent = "No se pudo crear: " + e.message;
    }
  });

// ====== Router ======
async function router() {
  const route = (location.hash.replace("#", "") || "/").trim();
  console.log("[app.router] route=", route);
  const isLogged = !!Auth.token;
  const role = userRole();

  configureNavbar();

  if (route === "/catalogo") {
    show("catalogo");
    await loadCatalogo();
    return;
  }
  if (route === "/proveedores") {
    if (!isLogged) {
      location.hash = "/login";
      return;
    }
    show("proveedores");
    await loadProveedores();
    return;
  }
  if (route === "/contratacion") {
    if (!isLogged) {
      location.hash = "/login";
      return;
    }
    show("contratacion");
    await loadContratacion();
    return;
  }
  if (route === "/login" && !isLogged) {
    show("login");
    // Mejoras UX: enfocar el email y animar la tarjeta de login
    try {
      const loginCard = document.querySelector('#view-login .login-card');
      const emailInput = document.querySelector('#login-form input[name="email"]');
      // Forzar reflow y aplicar clase para animación
      if (loginCard) {
        loginCard.classList.remove('showing');
        // next tick
        setTimeout(() => loginCard.classList.add('showing'), 30);
      }
      if (emailInput) {
        setTimeout(() => {
          try { emailInput.focus(); emailInput.select(); } catch (e) {}
        }, 160);
      }
    } catch (e) { /* silent */ }
    return;
  }
  if (route === "/admin-register") {
    if (!isLogged || role !== "ADMIN") {
      location.hash = "/";
      return;
    }
    show("adminRegister");
    return;
  }
  if (route === "/me") {
    if (!isLogged) {
      location.hash = "/login";
      return;
    }
    show("me");
    await loadMe();
    return;
  }
  if (route === "/admin") {
    if (!isLogged || role !== "ADMIN") {
      location.hash = "/";
      return;
    }
    adminOffset = 0;
    adminTotal = null;
    show("admin");
    await loadUsers();
    return;
  }
  show("home");
}

window.addEventListener("hashchange", router);

// ----- Boot -----
(async function init() {
  try {
    const reloadBtn = document.getElementById("btn-catalogo-reload");
    if (reloadBtn && !reloadBtn._bound) {
      reloadBtn.addEventListener("click", (ev) => {
        ev.preventDefault();
        loadCatalogo();
      });
      reloadBtn._bound = true;
    }

    const refreshPedidosBtn = document.getElementById("btn-refresh-pedidos");
    if (refreshPedidosBtn && !refreshPedidosBtn._bound) {
      refreshPedidosBtn.addEventListener("click", (ev) => {
        ev.preventDefault();
        refreshPedidos();
      });
      refreshPedidosBtn._bound = true;
    }

    const filterStatusCliente = document.getElementById("filter-status");
    if (filterStatusCliente && !filterStatusCliente._bound) {
      filterStatusCliente.addEventListener("change", () => {
        refreshMisPedidos();
      });
      filterStatusCliente._bound = true;
    }

    // Configurar eventos para admin pedidos
    const refreshAdminBtn = document.getElementById("btn-refresh-admin-pedidos");
    if (refreshAdminBtn && !refreshAdminBtn._bound) {
      refreshAdminBtn.addEventListener("click", refreshAdminPedidos);
      refreshAdminBtn._bound = true;
    }

    const filterStatus = document.getElementById("admin-filter-status");
    if (filterStatus && !filterStatus._bound) {
      filterStatus.addEventListener("change", aplicarFiltrosAdmin);
      filterStatus._bound = true;
    }

    // Filtro por email (debounced)
    const adminFilterEmail = document.getElementById("admin-filter-email");
    if (adminFilterEmail && !adminFilterEmail._bound) {
      let _admEmailTimeout = null;
      adminFilterEmail.addEventListener("input", (ev) => {
        if (_admEmailTimeout) clearTimeout(_admEmailTimeout);
        _admEmailTimeout = setTimeout(() => {
          adminOffset = 0; // resetear paginación al cambiar filtro
          loadUsers();
        }, 400);
      });
      adminFilterEmail._bound = true;
    }

    const clearFiltersBtn = document.getElementById("admin-clear-filters");
    if (clearFiltersBtn && !clearFiltersBtn._bound) {
      clearFiltersBtn.addEventListener("click", () => {
        document.getElementById("admin-filter-status").value = "";
        document.getElementById("admin-search-id").value = "";
        document.getElementById("admin-search-cliente").value = "";
        refreshAdminPedidos();
      });
      clearFiltersBtn._bound = true;
    }

    // Configurar formularios de modales ADMIN
    setupAdminModals();

    const me = await Auth.init(); // si hay token, intenta /me
    if (me) currentUser = me;
  } catch (e) {
    console.error("Error durante inicialización de la app", e);
  } finally {
    configureNavbar();
    router();
  }
})();
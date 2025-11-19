// js/app.js
import { Auth } from "./auth.js";
import { IAM, CATALOGO, getToken } from "./api.js";
import { PROVEEDORES, CONTRATACION } from "./services.js";

console.log("[app] module loaded");

let currentUser = null; // cache

// Admin pagination state
let adminLimit = 10;
let adminOffset = 0;
let adminTotal = null; // if backend provides total count

// Contratación pendiente (cuando viene desde catálogo sin login)
let pendingPaqueteId = null;

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

function showContratacionModal(paqueteId, paquete) {
    // Crear modal dinámico o usar uno existente
    const modalHtml = `
        <div class="modal fade" id="contratacionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Completar datos del evento</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="contratacion-modal-form">
                            <div class="mb-3">
                                <label class="form-label">Fecha del evento</label>
                                <input type="date" name="fecha_evento" class="form-control" required 
                                       min="${new Date().toISOString().split('T')[0]}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Hora de inicio</label>
                                <input type="time" name="hora_inicio" class="form-control" required value="18:00">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Hora de fin (opcional)</label>
                                <input type="time" name="hora_fin" class="form-control">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Ubicación</label>
                                <input type="text" name="ubicacion" class="form-control" required 
                                       placeholder="Dirección del evento">
                            </div>
                            <input type="hidden" name="paquete_id" value="${paqueteId}">
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" id="confirmar-contratacion">Confirmar Contratación</button>
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
            alert('Por favor complete todos los campos requeridos');
            return;
        }

        try {
            modal.hide();
            await doContratarPaquete(payload);
        } catch (error) {
            console.error('Error en contratación:', error);
        }
    });

    modal.show();
    
    // Limpiar modal cuando se cierre
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.remove();
    });
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
  await doContratarPaquete(id);
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
    list.forEach((p, idx) => {
      const col = document.createElement("div");
      col.className = "col-12 col-md-6 col-lg-4";

      const card = document.createElement("div");
      card.className = "card h-100 shadow-sm border-0";

      const body = document.createElement("div");
      body.className = "card-body d-flex flex-column";

      const title = document.createElement("h5");
      title.className = "card-title mb-1 text-truncate";
      title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;

      const desc = document.createElement("p");
      desc.className = "card-text small text-muted flex-grow-1";
      desc.textContent =
        p.descripcion || p.description || "Sin descripción.";

      const meta = document.createElement("div");
      meta.className = "mt-2 small";

      const servicios = p.servicios || p.services || [];
      if (Array.isArray(servicios) && servicios.length) {
        const label = document.createElement("div");
        label.className = "fw-semibold mb-1";
        label.textContent = "Servicios incluidos:";
        meta.appendChild(label);

        const ul = document.createElement("ul");
        ul.className = "small ps-3 mb-0";
        servicios.slice(0, 3).forEach((s) => {
          const li = document.createElement("li");
          li.textContent = s.nombre || s.name || String(s);
          ul.appendChild(li);
        });
        if (servicios.length > 3) {
          const li = document.createElement("li");
          li.textContent = `+ ${servicios.length - 3} adicionales`;
          ul.appendChild(li);
        }
        meta.appendChild(ul);
      }

      const footer = document.createElement("div");
      footer.className =
        "mt-3 d-flex justify-content-between align-items-center small";

      const price = document.createElement("span");
      const monto = p.precio ?? p.monto ?? p.amount;
      if (monto != null && !Number.isNaN(Number(monto))) {
        price.textContent = `Desde S/ ${Number(monto).toFixed(2)}`;
      } else {
        price.textContent = "Precio a consultar";
      }

      const btn = document.createElement("button");
      btn.className = "btn btn-sm btn-primary";
      btn.textContent = "Reservar / Contratar";
      btn.addEventListener("click", () =>
        solicitarContratacionDesdeCatalogo(p)
      );

      footer.appendChild(price);
      footer.appendChild(btn);

      body.appendChild(title);
      body.appendChild(desc);
      body.appendChild(meta);
      body.appendChild(footer);

      card.appendChild(body);
      col.appendChild(card);
      fragment.appendChild(col);
    });
    cardsRow.appendChild(fragment);

    // --- Carrusel basado en los mismos paquetes (resumen) ---
    if (carouselInner && carouselWrap) {
      list.forEach((p, idx) => {
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
        price.className = "fw-semibold mb-2";
        if (monto != null && !Number.isNaN(Number(monto))) {
          price.textContent = `Desde S/ ${Number(monto).toFixed(2)}`;
        } else {
          price.textContent = "Precio a consultar";
        }

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

      if (list.length > 1) {
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
        const data = await PROVEEDORES.buscar(
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
          const btn = document.createElement("button");
          btn.className = "btn btn-sm btn-outline-primary";
          btn.textContent = "Reservar";
          btn.addEventListener("click", async () => {
            try {
              const payload = {
                proveedor_id:
                  item.id || item.proveedor_id || item.proveedor || null,
                servicio_id: servicio_id || null,
                fecha,
              };
              await PROVEEDORES.crearReserva(payload);
              alert("Reserva creada correctamente.");
            } catch (e) {
              alert("Error al crear reserva: " + (e.message || e));
            }
          });
          right.appendChild(btn);
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
    const pedidoId = e.target.dataset.pedidoId;
    cambiarEstadoPedidoAdmin(pedidoId, nuevoEstado);
  });

  // Agregar eventos para los botones de acción
  const detalleBtn = item.querySelector('.ver-detalle-admin');
  detalleBtn.addEventListener('click', () => {
    verDetallePedidoAdmin(pedido.id);
  });

  const asignarBtn = item.querySelector('.asignar-proveedor');
  asignarBtn.addEventListener('click', () => {
    alert(`Asignar proveedor al pedido ${pedido.pedido_id || pedido.id} - Funcionalidad pendiente`);
  });

  const itemsBtn = item.querySelector('.agregar-items');
  itemsBtn.addEventListener('click', () => {
    alert(`Agregar items al pedido ${pedido.pedido_id || pedido.id} - Funcionalidad pendiente`);
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
                          <th>Servicio</th>
                          <th>Cantidad</th>
                          <th>Precio Unit.</th>
                          <th>Subtotal</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${pedido.items.map(item => `
                          <tr>
                            <td>${item.servicio_nombre || 'Servicio'}</td>
                            <td>${item.cantidad || 1}</td>
                            <td>${item.precio_unitario ? `S/ ${parseFloat(item.precio_unitario).toFixed(2)}` : 'N/A'}</td>
                            <td>${item.subtotal ? `S/ ${parseFloat(item.subtotal).toFixed(2)}` : 'N/A'}</td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                  </div>
                </div>
              ` : '<p class="text-muted">No hay items registrados en este pedido.</p>'}
              
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
      cambiarEstadoPedidoAdmin(pedidoId, nuevoEstado);
      modal.hide();
    });

    document.getElementById('modal-asignar-proveedor').addEventListener('click', () => {
      alert(`Asignar proveedor al pedido ${pedidoId} - Funcionalidad pendiente`);
    });

    document.getElementById('modal-agregar-items').addEventListener('click', () => {
      alert(`Gestionar items del pedido ${pedidoId} - Funcionalidad pendiente`);
    });

    modal.show();
    
    // Limpiar modal cuando se cierre
    modalElement.addEventListener('hidden.bs.modal', () => {
      modalElement.remove();
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
    const data = await IAM.adminUsers(adminLimit, adminOffset);
    const items = (data && data.items) ? data.items : data;
    adminTotal =
      data && (data.total || data.count || (data.meta && data.meta.total)) ||
      null;

    (items ?? []).forEach((u) => {
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
    });

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
    const u = await IAM.adminGetUser(id);
    form["id"].value = u.id;
    form["nombre"].value = u.nombre || "";
    form["telefono"].value = u.telefono || "";
    form["role"].value = u.role || "CLIENTE";
    form["status"].value = String(u.status ?? 1);
    if (form["password"]) form["password"].value = "";
    editUserModal?.show();
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
  } else if (role === "ADMIN") {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#/admin-register");
    navRegister?.setAttribute("data-mode", "admin");
    navAdmin?.classList.remove("d-none");
  } else {
    navRegister?.classList.add("d-none");
    navRegister?.setAttribute("data-mode", "hidden");
    navAdmin?.classList.add("d-none");
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

    const me = await Auth.init(); // si hay token, intenta /me
    if (me) currentUser = me;
  } catch (e) {
    console.error("Error durante inicialización de la app", e);
  } finally {
    configureNavbar();
    router();
  }
})();
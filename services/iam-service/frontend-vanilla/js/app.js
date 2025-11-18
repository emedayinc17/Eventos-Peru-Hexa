// js/app.js
import { Auth } from "./auth.js";
import {IAM} from "./api.js";
import {PROVEEDOR} from "./api-proveedores.js";

let currentUser = null; // cache

// Admin pagination state
let adminLimit = 10;
let adminOffset = 0;
let adminTotal = null; // if backend provides total count

// Proveedor
let proveedorSeleccionado = null;
let reservasActivas = [];
let crearReservaModal = null;

// ----- refs de vistas -----
const views = {
  home:            document.getElementById("view-home"),
  login:           document.getElementById("view-login"),
  adminRegister:   document.getElementById("view-admin-register"),
  me:              document.getElementById("view-me"),
  admin:           document.getElementById("view-admin"),
  proveedores:     document.getElementById("view-proveedores")
};

// ----- navbar -----
const navLogin    = document.getElementById("nav-login");
const navLogout   = document.getElementById("nav-logout");
const navRegister = document.getElementById("nav-register");
const navAdmin    = document.getElementById("nav-admin");
const navProveedores    = document.getElementById("nav-proveedores");
const openPublicRegister = document.getElementById("open-public-register");

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
  Object.values(views).forEach(v => v?.classList.add("d-none"));
  (views[id] ?? views.home)?.classList.remove("d-none");
  try { window.scrollTo({ top: 0, behavior: "smooth" }); } catch {}
}
const roleOf = u => (u?.role || "").toString().toUpperCase();
const userRole = () => roleOf(currentUser);

// ----- PERFIL -----
async function loadMe() {
  const pre      = document.getElementById("me-json");
  const nameEl   = document.getElementById("me-name");
  const emailEl  = document.getElementById("me-email");
  const idEl     = document.getElementById("me-id");
  const telEl    = document.getElementById("me-telefono");
  const roleEl   = document.getElementById("me-role");
  const statusEl = document.getElementById("me-status");
  const avatarEl = document.getElementById("me-avatar");

  try {
    const u = await Auth.me();
    currentUser = u;
    if (pre) pre.textContent = JSON.stringify(u, null, 2);

    const nombre = u.nombre || "";
    const email  = u.email || "";
    const role   = roleOf(u);
    const tel    = u.telefono || "—";
    const activo = Number(u.status) === 1;

    const initials = (() => {
      const base = (nombre || email.split("@")[0] || "").trim();
      const parts = base.split(/\s+/);
      const a = (parts[0]?.[0] || "").toUpperCase();
      const b = (parts[1]?.[0] || "").toUpperCase();
      return (a + b) || (a || "?");
    })();

    if (avatarEl) avatarEl.textContent = initials;
    if (nameEl) nameEl.textContent = nombre || email;
    if (emailEl) emailEl.textContent = email;
    if (idEl) idEl.textContent = u.id || "—";
    if (telEl) telEl.textContent = tel;
    if (roleEl) {
      roleEl.textContent = role || "—";
      roleEl.className = "ms-auto badge rounded-pill " + (role === "ADMIN" ? "text-bg-primary" : "text-bg-info");
    }
    if (statusEl) {
      statusEl.textContent = activo ? "ACTIVO" : "INACTIVO";
      statusEl.className = "badge rounded-pill " + (activo ? "text-bg-success" : "text-bg-secondary");
    }
  } catch (e) {
    if (pre) { pre.classList.remove("d-none"); pre.textContent = "Error: " + e.message; }
  }
}

// ----- ADMIN LISTA -----
// Admin / Users con iconos de acción
async function loadUsers() {
  const tbody = document.getElementById("users-tbody");
  const err = document.getElementById("admin-error");
  tbody.innerHTML = "";
  err.textContent = "";
  try {
    const data = await IAM.adminUsers(adminLimit, adminOffset);
    // Detect items array (paginated) or array directly
    const items = (data && data.items) ? data.items : data;
    // Try to read total count if backend provides it
    adminTotal = data && (data.total || data.count || (data.meta && data.meta.total)) || null;

    (items ?? []).forEach(u => {
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

    // Listeners para iconos
    tbody.querySelectorAll(".edit-user").forEach(btn => {
      btn.addEventListener("click", async e => {
        const id = e.currentTarget.dataset.id;
        await openEditModal(id);
      });
    });

    tbody.querySelectorAll(".delete-user").forEach(btn => {
      btn.addEventListener("click", async e => {
        const id = e.currentTarget.dataset.id;
        confirmDeleteUser(id);
      });
    });

  } catch (e) {
    err.textContent = "No autorizado o error: " + e.message;
  }

  // Render pagination controls
  renderAdminPagination();
}

function renderAdminPagination() {
  const container = document.getElementById("admin-pagination");
  const info = document.getElementById("admin-pagination-info");
  if (!container || !info) return;

  // Clear
  container.innerHTML = "";

  // Prev button
  const btnPrev = document.createElement("button");
  btnPrev.className = "btn btn-sm btn-outline-secondary";
  btnPrev.textContent = "« Prev";
  btnPrev.disabled = adminOffset <= 0;
  btnPrev.addEventListener("click", async () => {
    if (adminOffset <= 0) return;
    adminOffset = Math.max(0, adminOffset - adminLimit);
    await loadUsers();
  });

  // Next button
  const btnNext = document.createElement("button");
  btnNext.className = "btn btn-sm btn-outline-secondary";
  btnNext.textContent = "Next »";
  // If we know total we can disable when end reached; otherwise enable if items length == limit
  let disableNext = false;
  if (adminTotal !== null) {
    disableNext = adminOffset + adminLimit >= adminTotal;
  }
  btnNext.disabled = disableNext;
  btnNext.addEventListener("click", async () => {
    // If total known, avoid overshooting
    if (adminTotal !== null && adminOffset + adminLimit >= adminTotal) return;
    adminOffset = adminOffset + adminLimit;
    await loadUsers();
  });

  container.appendChild(btnPrev);
  container.appendChild(btnNext);

  // Info text
  const page = Math.floor(adminOffset / adminLimit) + 1;
  const from = adminOffset + 1;
  const to = adminOffset + adminLimit;
  if (adminTotal !== null) {
    info.textContent = `Página ${page} — mostrando ${from}-${Math.min(to, adminTotal)} de ${adminTotal}`;
  } else {
    info.textContent = `Página ${page} — items ${from}-${to}`;
  }
}

// Modal para editar usuario
let editUserModal = null;
function ensureEditModal() {
  if (!editUserModal) {
    const el = document.getElementById("editUserModal");
    if (el && window.bootstrap?.Modal) editUserModal = new bootstrap.Modal(el);
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
    // Clear password field (do not prefill)
    if (form["password"]) form["password"].value = "";
    editUserModal?.show();
  } catch (e) {
    alert("Error al cargar usuario: " + e.message);
  }
}

document.getElementById("edit-user-form")?.addEventListener("submit", async ev => {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const id = fd.get("id");
  const patch = {
    nombre: fd.get("nombre") || "",
    telefono: fd.get("telefono") || "",
    status: Number(fd.get("status")),
    role: fd.get("role") || "CLIENTE",
  };
  // If password provided, include in patch
  const pw = (fd.get("password") || "").toString();
  if (pw && pw.length > 0) patch.password = pw;
  const err = document.getElementById("edit-error");
  err.textContent = "";
  try {
    await IAM.adminPatchUser(id, patch);
    editUserModal?.hide();
    await loadUsers();
  } catch (e) {
    err.textContent = "No se pudo actualizar: " + e.message;
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


// ----- LOGIN -----
document.getElementById("login-form")?.addEventListener("submit", async (ev) => {
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
    configureNavbar();   // actualiza registrar según rol
    location.hash = "/me";
  } catch (e) { err.textContent = "Credenciales inválidas o error de servidor."; }
});

// ----- LOGOUT -----
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
document.getElementById("btn-admin-reload")?.addEventListener("click", (e) => {
  e.preventDefault(); loadUsers();
});

// ----- Abrir modal desde link en Login -----
openPublicRegister?.addEventListener("click", (e) => {
  e.preventDefault(); ensurePublicModal(); publicRegisterModal?.show();
});

// ======= NAVBAR SMART =======
function configureNavbar() {
  const isLogged = !!Auth.token;
  const role = userRole();

  // Login / Logout
  navLogin?.classList.toggle("d-none", isLogged);
  navLogout?.classList.toggle("d-none", !isLogged);

  // Registrar — control por data-mode
  if (!isLogged) {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#");          // no navegamos de hash
    navRegister?.setAttribute("data-mode", "public");
    // admin link hidden when not logged
    navAdmin?.classList.add("d-none");
    navProveedores?.classList.add("d-none");
  } else if (role === "ADMIN") {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#/admin-register");
    navRegister?.setAttribute("data-mode", "admin");
    // Only show admin nav to ADMIN role
    navAdmin?.classList.remove("d-none");
    navProveedores?.classList.remove("d-none");
  } else {
    navRegister?.classList.add("d-none");
    navRegister?.setAttribute("data-mode", "hidden");
    // Non-admin logged-in users should not see the Admin link
    navAdmin?.classList.add("d-none");
    navProveedores?.classList.remove("d-none");
  }
}

// Un SOLO listener para Registrar, decide por data-mode
navRegister?.addEventListener("click", (e) => {
  const mode = navRegister.getAttribute("data-mode");
  if (mode === "public") {
    e.preventDefault();
    ensurePublicModal(); publicRegisterModal?.show();
  }
  // mode === "admin" => dejamos navegar a #/admin-register
  // mode === "hidden" => no habrá botón visible
});

// ----- Registro PÚBLICO (modal) -----
document.getElementById("public-register-form")?.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const email    = (fd.get("email") || "").toString();
  const password = (fd.get("password") || "").toString();
  const nombre   = (fd.get("nombre") || "").toString();
  const telefono = (fd.get("telefono") || "").toString();
  const err = document.getElementById("public-register-error");
  err.textContent = "";
  try {
    await IAM.register(email, password, nombre, telefono);
    ensurePublicModal(); publicRegisterModal?.hide();
    location.hash = "/login";
    setTimeout(() => {
      const emailInput = document.querySelector('#login-form input[name="email"]');
      if (emailInput) emailInput.value = email;
    }, 50);
  } catch (e) { err.textContent = "No se pudo registrar: " + e.message; }
});

// ----- Registro ADMIN -----
document.getElementById("admin-create-form")?.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const payload = {
    email:    (fd.get("email") || "").toString(),
    password: (fd.get("password") || "").toString(),
    nombre:   (fd.get("nombre") || "").toString(),
    telefono: (fd.get("telefono") || "").toString(),
    role:     (fd.get("role") || "").toString().toUpperCase() || "CLIENTE",
  };
  const err = document.getElementById("admin-create-error");
  const ok  = document.getElementById("admin-create-ok");
  err.textContent = ""; ok?.classList.add("d-none");
  try {
    await IAM.adminCreateUser(payload);
    ok?.classList.remove("d-none");
    (ev.target).reset();
  } catch (e) { err.textContent = "No se pudo crear: " + e.message; }
});

// ==========================================
// Proveedores
// ==========================================
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
    const proveedores = await PROVEEDOR.buscarDisponibles(servicioId, fecha);

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

  try {
    const reserva = await PROVEEDOR.registroReserva(data);
    crearReservaModal?.hide();
    alert(`Reserva creada exitosamente!\nID: ${reserva.id}\nExpira: ${reserva.expira_en}`);

    // Limpiar formulario
    e.target.reset();

    // Si está en la vista de reservas, recargar
    if (!views.reservas.classList.contains("d-none")) {
      cargarReservas();
    }
  } catch (error) {
    err.textContent = "Error: " + error.message;
  }
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

// ----- Router -----
async function router() {
  const route = (location.hash.replace("#", "") || "/").trim();
  const isLogged = !!Auth.token;
  const role = userRole();

  configureNavbar();

  if (route === "/login" && !isLogged) { show("login"); return; }
  if (route === "/admin-register") {
    if (!isLogged || role !== "ADMIN") { location.hash = "/"; return; }
    show("adminRegister"); return;
  }
  if (route === "/me") {
    if (!isLogged) { location.hash = "/login"; return; }
    show("me"); await loadMe(); return;
  }
  if (route === "/admin") {
    if (!isLogged || role !== "ADMIN") { location.hash = "/"; return; }
    // Reset to first page when opening admin view
    adminOffset = 0;
    adminTotal = null;
    show("admin"); await loadUsers(); return;
  }
  if (route === "/proveedores" || route === "proveedores") {
    if (!isLogged) { location.hash = "/login"; return; }
    show("proveedores"); return;
  }
  show("home");
}

window.addEventListener("hashchange", router);

// ----- Boot -----
(async function init() {
  try {
    const me = await Auth.init(); // si hay token, intenta /me
    if (me) currentUser = me;
  } catch (e) {
    console.error("Error durante inicialización de la app", e);
  } finally {
    configureNavbar();
    router();
  }
})();

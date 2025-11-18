// js/app.js
import { Auth } from "./auth.js";
import { IAM, CATALOGO, getToken } from "./api.js";
import { PROVEEDORES, CONTRATACION } from "./services.js";

console.log('[app] module loaded');

let currentUser = null; // cache

// Admin pagination state
let adminLimit = 10;
let adminOffset = 0;
let adminTotal = null; // if backend provides total count

// ----- refs de vistas -----
const views = {
  home:            document.getElementById("view-home"),
  catalogo:        document.getElementById("view-catalogo"),
  login:           document.getElementById("view-login"),
  adminRegister:   document.getElementById("view-admin-register"),
  me:              document.getElementById("view-me"),
  admin:           document.getElementById("view-admin"),
  proveedores:     document.getElementById("view-proveedores"),
  contratacion:    document.getElementById("view-contratacion"),
};

// ----- navbar -----
const navLogin    = document.getElementById("nav-login");
const navCatalogo = document.getElementById("nav-catalogo");
const navLogout   = document.getElementById("nav-logout");
const navRegister = document.getElementById("nav-register");
const navAdmin    = document.getElementById("nav-admin");
const openPublicRegister = document.getElementById("open-public-register");

// Safety: ensure navbar links trigger routing even if default hashchange is blocked
function bindNavLink(id, hash) {
  const el = document.getElementById(id);
  if (!el) { console.log(`[app] nav element not found: ${id}`); return; }
  el.addEventListener('click', (ev) => {
    // allow the anchor default for normal navigation but also force routing
    try { ev.preventDefault(); } catch {}
    try { location.hash = hash; } catch {}
    try { router(); } catch (e) { console.error('router error (nav click)', e); }
  });
}
bindNavLink('nav-catalogo', '#/catalogo');
bindNavLink('nav-proveedores', '#/proveedores');
bindNavLink('nav-contratacion', '#/contratacion');

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

// ----- CATÁLOGO -----
// Renderiza tarjetas y carrusel a partir de la lista de paquetes.
async function loadCatalogo() {
  const alertBox      = document.getElementById("catalogo-alert");
  const cardsRow      = document.getElementById("catalogo-cards");
  const carouselWrap  = document.getElementById("catalogo-carousel-wrapper");
  const carouselInner = document.getElementById("catalogo-carousel-inner");
  const reloadBtn     = document.getElementById("btn-catalogo-reload");

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
    const list = Array.isArray(paquetes) ? paquetes : (paquetes?.items ?? []);

    if (!list.length) {
      if (alertBox) {
        alertBox.className = "alert alert-warning";
        alertBox.textContent = "No hay paquetes configurados en el catálogo.";
        alertBox.classList.remove("d-none");
      }
      return;
    }

    if (alertBox) alertBox.classList.add("d-none");

    // Tarjetas
    const fragment = document.createDocumentFragment();
    list.forEach((p, idx) => {
      const col = document.createElement("div");
      col.className = "col-12 col-md-6 col-lg-4";

      const card = document.createElement("div");
      card.className = "card h-100 shadow-sm";

      const body = document.createElement("div");
      body.className = "card-body d-flex flex-column";

      const title = document.createElement("h5");
      title.className = "card-title";
      title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;

      const desc = document.createElement("p");
      desc.className = "card-text small text-muted flex-grow-1";
      desc.textContent = p.descripcion || p.description || "Sin descripción.";

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
        servicios.slice(0, 4).forEach(s => {
          const li = document.createElement("li");
          li.textContent = s.nombre || s.name || String(s);
          ul.appendChild(li);
        });
        if (servicios.length > 4) {
          const li = document.createElement("li");
          li.textContent = `+ ${servicios.length - 4} adicionales`;
          ul.appendChild(li);
        }
        meta.appendChild(ul);
      }

      const footer = document.createElement("div");
      footer.className = "mt-3 d-flex justify-content-between align-items-center small";

      const price = document.createElement("span");
      const monto = p.precio ?? p.monto ?? p.amount;
      if (monto != null && !Number.isNaN(Number(monto))) {
        price.textContent = `Desde S/ ${Number(monto).toFixed(2)}`;
      } else {
        price.textContent = "Precio a consultar";
      }

      const badge = document.createElement("span");
      badge.className = "badge text-bg-primary";
      badge.textContent = p.codigo || p.code || p.id || `PK-${idx + 1}`;

      footer.appendChild(price);
      footer.appendChild(badge);

      body.appendChild(title);
      body.appendChild(desc);
      body.appendChild(meta);
      body.appendChild(footer);

      card.appendChild(body);
      col.appendChild(card);
      fragment.appendChild(col);
    });
    cardsRow.appendChild(fragment);

    // Carrusel basado en los mismos paquetes
    if (carouselInner && carouselWrap) {
      list.forEach((p, idx) => {
        const item = document.createElement("div");
        item.className = "carousel-item" + (idx === 0 ? " active" : "");

        const inner = document.createElement("div");
        inner.className = "d-flex flex-column justify-content-center align-items-start p-4 bg-white border rounded-3 shadow-sm";
        inner.style.minHeight = "160px";

        const title = document.createElement("h5");
        title.className = "mb-1";
        title.textContent = p.nombre || p.name || `Paquete ${idx + 1}`;

        const desc = document.createElement("p");
        desc.className = "mb-2 small text-muted";
        desc.textContent = p.descripcion || p.description || "Sin descripción.";

        const meta = document.createElement("div");
        meta.className = "small text-secondary";
        const servicios = p.servicios || p.services || [];
        if (Array.isArray(servicios) && servicios.length) {
          meta.textContent = `Incluye ${servicios.length} servicio(s).`;
        } else {
          meta.textContent = "Servicios no detallados.";
        }

        inner.appendChild(title);
        inner.appendChild(desc);
        inner.appendChild(meta);
        item.appendChild(inner);
        carouselInner.appendChild(item);
      });

      if (list.length > 1) {
        carouselWrap.classList.remove("d-none");
      } else {
        carouselWrap.classList.add("d-none");
      }
    }

  } catch (err) {
    console.error("Error cargando catálogo", err);
    if (alertBox) {
      alertBox.className = "alert alert-danger";
      alertBox.textContent = "No se pudo cargar el catálogo. Intenta más tarde.";
      alertBox.classList.remove("d-none");
    }
  } finally {
    const reloadBtn2 = document.getElementById("btn-catalogo-reload");
    if (reloadBtn2) reloadBtn2.disabled = false;
  }
}

// ----- PROVEEDORES -----
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
        const data = await PROVEEDORES.buscar(servicio_id || null, fecha || "", limit, 0);
        const list = Array.isArray(data) ? data : (data?.items ?? []);
        if (!list.length) { err.textContent = "No se encontraron proveedores/disponibilidades."; return; }
        const frag = document.createDocumentFragment();
        list.forEach(item => {
          const a = document.createElement("div");
          a.className = "list-group-item d-flex justify-content-between align-items-start";
          const left = document.createElement("div");
          left.innerHTML = `<div class="fw-semibold">${item.nombre || item.name || item.proveedor || 'Proveedor'}</div><div class="small text-muted">${item.descripcion || item.desc || ''}</div>`;
          const right = document.createElement("div");
          const btn = document.createElement("button");
          btn.className = "btn btn-sm btn-outline-primary";
          btn.textContent = "Reservar";
          btn.addEventListener("click", async () => {
            try {
              const payload = { proveedor_id: item.id || item.proveedor_id || item.proveedor || null, servicio_id: servicio_id || null, fecha };
              await PROVEEDORES.crearReserva(payload);
              alert('Reserva creada correctamente.');
            } catch (e) { alert('Error al crear reserva: ' + (e.message || e)); }
          });
          right.appendChild(btn);
          a.appendChild(left);
          a.appendChild(right);
          frag.appendChild(a);
        });
        results.appendChild(frag);
      } catch (e) {
        console.error('Error buscando proveedores', e);
        err.textContent = e.message || 'Error al consultar proveedores';
      }
    });
    form._bound = true;
  }
}

// ----- CONTRATACION -----
async function loadContratacion() {
  const form = document.getElementById("contratacion-create-form");
  const listWrap = document.getElementById("contratacion-mis-pedidos");
  const err = document.getElementById("contratacion-error");
  if (!form || !listWrap) return;
  err.textContent = "";
  listWrap.innerHTML = "";

  if (!form._bound) {
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      err.textContent = "";
      const fd = new FormData(form);
      const paquete_id = (fd.get("paquete_id") || "").toString().trim();
      const cantidad = Number(fd.get("cantidad") || 1) || 1;
      try {
        const body = { paquete_id, cantidad };
        const created = await CONTRATACION.crearPedido(body);
        alert('Pedido creado: ' + (created && created.id ? created.id : 'OK'));
        form.reset();
        await refreshMisPedidos(listWrap, err);
      } catch (e) {
        console.error('Error creando pedido', e);
        err.textContent = e.message || 'No se pudo crear pedido';
      }
    });
    form._bound = true;
  }

  await refreshMisPedidos(listWrap, err);
}

async function refreshMisPedidos(listWrap, err) {
  listWrap.innerHTML = "";
  err.textContent = "";
  try {
    const pedidos = await CONTRATACION.misPedidos();
    const arr = Array.isArray(pedidos) ? pedidos : (pedidos?.items ?? []);
    if (!arr.length) { listWrap.innerHTML = '<div class="text-muted small">No hay pedidos.</div>'; return; }
    const frag = document.createDocumentFragment();
    arr.forEach(p => {
      const a = document.createElement('div');
      a.className = 'list-group-item d-flex justify-content-between align-items-start';
      a.innerHTML = `<div><div class="fw-semibold">Pedido ${p.id || ''}</div><div class="small text-muted">${p.status || ''} — ${p.created_at || ''}</div></div>`;
      frag.appendChild(a);
    });
    listWrap.appendChild(frag);
  } catch (e) {
    console.error('Error cargando mis pedidos', e);
    err.textContent = e.message || 'Error al cargar pedidos';
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
  } else if (role === "ADMIN") {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#/admin-register");
    navRegister?.setAttribute("data-mode", "admin");
    // Only show admin nav to ADMIN role
    navAdmin?.classList.remove("d-none");
  } else {
    navRegister?.classList.add("d-none");
    navRegister?.setAttribute("data-mode", "hidden");
    // Non-admin logged-in users should not see the Admin link
    navAdmin?.classList.add("d-none");
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

// ----- Router -----
async function router() {
  const route = (location.hash.replace("#", "") || "/").trim();
  console.log('[app.router] route=', route);
  const isLogged = !!Auth.token;
  const role = userRole();

  configureNavbar();

  if (route === "/catalogo") {
    show("catalogo"); await loadCatalogo(); return;
  }
  if (route === "/proveedores") {
    // require login to view providers (they need token for availability)
    if (!isLogged) { location.hash = "/login"; return; }
    show("proveedores"); await loadProveedores(); return;
  }
  if (route === "/contratacion") {
    if (!isLogged) { location.hash = "/login"; return; }
    show("contratacion"); await loadContratacion(); return;
  }
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
  show("home");
}

window.addEventListener("hashchange", router);

// ----- Boot -----
(async function init() {
  try {
    // Hook botón de recarga de catálogo (si existe)
    const reloadBtn = document.getElementById("btn-catalogo-reload");
    if (reloadBtn) {
      reloadBtn.addEventListener("click", (ev) => {
        ev.preventDefault();
        loadCatalogo();
      });
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

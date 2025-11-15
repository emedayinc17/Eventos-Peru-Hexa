// js/app.js
import { Auth } from "./auth.js";
import { IAM } from "./api.js";

let currentUser = null; // cache

// ----- refs de vistas -----
const views = {
  home:            document.getElementById("view-home"),
  login:           document.getElementById("view-login"),
  adminRegister:   document.getElementById("view-admin-register"),
  me:              document.getElementById("view-me"),
  admin:           document.getElementById("view-admin"),
};

// ----- navbar -----
const navLogin    = document.getElementById("nav-login");
const navLogout   = document.getElementById("nav-logout");
const navRegister = document.getElementById("nav-register");
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
    const data = await IAM.adminUsers(50, 0);
    (data.items ?? data).forEach(u => {
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
  } else if (role === "ADMIN") {
    navRegister?.classList.remove("d-none");
    navRegister?.setAttribute("href", "#/admin-register");
    navRegister?.setAttribute("data-mode", "admin");
  } else {
    navRegister?.classList.add("d-none");
    navRegister?.setAttribute("data-mode", "hidden");
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
    show("admin"); await loadUsers(); return;
  }
  show("home");
}

window.addEventListener("hashchange", router);

// ----- Boot -----
(async function init() {
  const me = await Auth.init(); // si hay token, intenta /me
  if (me) currentUser = me;
  configureNavbar();
  router();
})();

//===== CONFIG =====
const BASE = "http://127.0.0.1:8040";
const OPENAPI_URL = `${BASE}/openapi.json`;
const LAST_USED_STATUS = "last_admin_status";
const ADMIN_STORAGE_KEY = "token_contratacion_admin";

const EXAMPLE_PROVEEDORES = [
    { id: "ccccccc0-cccc-cccc-cccc-ccccccccccc0", nombre: "Proveedor Alpha" },
    { id: "ccccccc1-cccc-cccc-cccc-ccccccccccc1", nombre: "Proveedor Beta" },
    { id: "ccccccc2-cccc-cccc-cccc-ccccccccccc2", nombre: "Proveedor Gamma"}
];

const CLIENTE_STORAGE_KEY_MANUAL = "token_contratacion_cliente";

function saveTokenCliente(t) {
  localStorage.setItem(CLIENTE_STORAGE_KEY_MANUAL, t);
}
function getTokenCliente() {
  return localStorage.getItem(CLIENTE_STORAGE_KEY_MANUAL) || "";
}

 function getStorageKey() {
    // Si estamos en la página de Admin, usamos una clave separada
    if (window.location.pathname.includes('admin.html')) {
      return "token_contratacion_admin";
    }
    // Por defecto Cliente  index.html
    return "token_contratacion_cliente";
  }

  function saveToken(t) { 
    localStorage.setItem(getStorageKey(), t); 
  }

  function getToken() { 
    return localStorage.getItem(getStorageKey()) || ""; 
  }

// ===== JWT ROLE DETECTION =====
function getUserRole() {
  const token = getToken();
  if (!token.includes(".")) return "guest";
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.role ? payload.role.toLowerCase() : "guest";
  } catch {
    return "guest";
  }
}

/// ===== FETCH CON AUTH (ACTUALIZADO) =====
async function callAuth(url, method = "GET", body = null) {
  const headers = { "Accept": "application/json" };
  if (getToken()) headers["Authorization"] = `Bearer ${getToken()}`;
  if (body) headers["Content-Type"] = "application/json";

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });

    const text = await response.text();
    showResponseModal(formatJSON(text), response.status);
  } catch (error) {
    showResponseModal(`❌ Error de red: ${error.message}`, 0);
  }
}

// ===== UI INIT =====
document.addEventListener("DOMContentLoaded", loadApp);

async function loadApp() {
  document.getElementById("btn-authorize").onclick = () => showTokenModal();
  loadEndpoints();
}

// ===== LOAD ENDPOINTS =====
async function loadEndpoints() {
  const container = document.getElementById("endpoints");
  const role = getUserRole();

  container.innerHTML = `<div class="col-12">Cargando endpoints para <b>${role}</b>...</div>`;

  try {
    const openapi = await (await fetch(OPENAPI_URL)).json();
    const endpoints = [];

    for (const path in openapi.paths) {
      if (path.includes("/contratacion/v1/contratacion/admin/pedidos/{pedido_id}/items")) continue;

      for (const method in openapi.paths[path]) {
        if (path.includes("/admin/"))
          endpoints.push({
            method: method.toUpperCase(),
            path,
            summary: openapi.paths[path][method].summary || "",
            isAdmin: true,
            secured: !!openapi.paths[path][method].security
          });
      }
    }

    // Endpoints de CLIENTE 
    for (const path in openapi.paths) { 
      // Excluir endpoints de Admin, debug, health, etc. [AÑADIDO PARA CLIENTE]
      if (path.includes("/contratacion/v1/contratacion/admin/")) continue; // [AÑADIDO PARA CLIENTE]
      if (path.includes("/contratacion/v1/contratacion/pedidos/{pedido_id}/enviar-resumen")) continue; // [AÑADIDO PARA CLIENTE]
      if (path.includes("/contratacion/_debug/")) continue; // [AÑADIDO PARA CLIENTE]
      if (path.includes("/contratacion/health")) continue; // [AÑADIDO PARA CLIENTE]
      
      for (const method in openapi.paths[path]) { // [AÑADIDO PARA CLIENTE]
        if (method.toUpperCase() === "POST" && path === "/contratacion/v1/contratacion/pedidos") {
          continue;
        }
        // Asegurarse de que no estamos cargando una ruta de Admin que ya se cargó arriba
        if (!path.includes("/admin/")) { // [AÑADIDO PARA CLIENTE]
          endpoints.push({
            method: method.toUpperCase(),
            path,
            summary: openapi.paths[path][method].summary || "",
            isAdmin: false, // Es importante que sea 'false' para que se renderice como cliente
            secured: !!openapi.paths[path][method].security
         });
        }
   }
  }

    container.innerHTML = "";
    endpoints.forEach(ep => renderEndpoint(ep, role));


  } catch (err) {
    container.innerHTML = `<div class="col-12 text-danger">❌ Error cargando OpenAPI: ${err.message}</div>`;
  }
}

// app.js (Reemplazar la función renderEndpoint)
function renderEndpoint(ep, role) {
  const container = document.getElementById("endpoints");

  const color =
    ep.method === "GET" ? "m-get"
    : ep.method === "POST" ? "m-post"
    : ep.method === "DELETE" ? "m-delete"
    : "m-patch";

  const disabled = "";
  const badge = ep.isAdmin ? `<span class="badge bg-danger ms-2">ADMIN</span>` : "";

  let displayTitle = ep.summary || ep.path;

  if (ep.path.includes("/admin/pedidos/{pedido_id}/items")) {
    displayTitle = "Añadir Ítems al Pedido";
  } else if (ep.path.includes("/admin/pedidos/{pedido_id}/asignar-proveedor")) {
    displayTitle = "Asignar Proveedor";
  } else if (ep.path.includes("/admin/pedidos/{pedido_id}")) {
    displayTitle = "Actualizar Estado del Pedido";
  }

  let buttonHTML;
  const requiresId = ep.path.includes("{pedido_id}");
  const requiresBody = ["POST", "PATCH", "PUT"].includes(ep.method);

  let buttonText = ep.summary || "Try It";

  if (ep.path.includes("/admin/pedidos/{pedido_id}")) {
    if (ep.method === "PATCH") buttonText = "Cambiar Estado";
    if (ep.path.includes("/items")) buttonText = "Añadir Ítems";
    if (ep.path.includes("/asignar-proveedor")) buttonText = "Asignar";
  }

  if (requiresId) {
    buttonHTML = `<div class="d-grid">
        <button class="btn btn-outline-warning btn-sm"
        onclick="askForPedidoAndExecute('${ep.method}', '${ep.path}', ${requiresBody})">
        ${buttonText}</button></div>`;
  } else {
    buttonHTML = `<div class="d-grid">
        <button class="btn btn-outline-primary btn-sm w-100"
        onclick="tryEndpoint('${ep.method}', '${ep.path}')">
        ${buttonText}</button></div>`;
  }

  container.insertAdjacentHTML(
    "beforeend",
    `<div class="col-12">
        <div class="card p-3 card-endpoint ${disabled}">
            <div class="d-flex justify-content-between">
                <div>
                    <span class="method-badge ${color}">${ep.method}</span>
                    <span class="ms-2">${displayTitle}</span>
                    ${badge}
                </div>
                ${buttonHTML}
            </div>
        </div>
    </div>`
  );
}

// ===== TRY ENDPOINT =====
async function tryEndpoint(method, path) {
  const url = BASE + path;

  if (["POST", "PATCH", "PUT"].includes(method)) {
    showBodyModal(path, async body => await callAuth(url, method, body));
  } else {
    await callAuth(url, method);
  }
}

// ===== MODALS =====
function showTokenModal() {
  document.getElementById("auth-token").value = getToken();
  const modal = new bootstrap.Modal(document.getElementById("authModal"));
  modal.show();

  document.getElementById("btn-save-token").onclick = () => {
    saveToken(document.getElementById("auth-token").value.trim());
    modal.hide();
    loadEndpoints();
  };
}

function createAsignarProveedorBody() {
  return JSON.stringify({
    "proveedor_id": "ccccccc2-cccc-cccc-cccc-ccccccccccc2",
    "fecha_inicio": "2025-11-14T12:00:00Z",
    "fecha_fin": "2025-11-16T12:00:00Z",
    "correlation_id": "HOLD2"
  }, null, 2);
}

function showBodyModal(path, callback) {
  const modal = new bootstrap.Modal(document.getElementById("bodyModal"));
  const textarea = document.getElementById("body-json");

  if (path.includes("/asignar-proveedor")) {
    textarea.value = JSON.stringify({
      proveedor_id: "ccccccc2-cccc-cccc-cccc-ccccccccccc2",
      fecha_inicio: "2025-11-14T12:00:00Z",
      fecha_fin: "2025-11-16T12:00:00Z",
      correlation_id: "HOLD2"
    }, null, 2);
  }
  else if (path.includes("/admin/pedidos")) {
    const ultimoEstado = localStorage.getItem("last_admin_status") || 0;
    textarea.value = JSON.stringify({ estado: parseInt(ultimoEstado) }, null, 2);
  }
  else {
    textarea.value = JSON.stringify({ campo: "valor" }, null, 2);
  }

  modal.show();

  document.getElementById("btn-send-body").onclick = async () => {
    const raw = textarea.value.trim();
    try {
      const json = raw ? JSON.parse(raw) : {};

      if (path.includes("/admin/pedidos") && json.estado !== undefined) {
        localStorage.setItem("last_admin_status", json.estado.toString());
      }

      modal.hide();
      await callback(json);
    } catch (e) {
      alert("❌ JSON inválido. Revisa el formato.");
    }
  };
}

// ===== MODAL DE RESPUESTA =====
function showResponseModal(content, status) {
  const modal = new bootstrap.Modal(document.getElementById("responseModal"));
  document.getElementById("response-content").innerText = content;

  const titleElement = document.querySelector("#responseModal .modal-title");
  titleElement.innerHTML = status
    ? `Respuesta de la API (${status})`
    : `Respuesta de la API`;

  modal.show();
}

// ===== JSON FORMATTER =====
function formatJSON(text) {
  try {
    return JSON.stringify(JSON.parse(text), null, 2);
  } catch {
    return text;
  }
}

async function showDynamicIdModal(method, path) {
  const idParam = "{pedido_id}";
  const pedidoId = prompt(`Por favor, ingresa el ID del Pedido para: ${path}`);

  if (pedidoId) {
    const finalPath = path.replace(idParam, pedidoId);
    const url = BASE + finalPath;

    if (["POST", "PATCH", "PUT"].includes(method)) {
      showBodyModal(finalPath, async body => await callAuth(url, method, body));
    } else {
      await callAuth(url, method);
    }
  } else if (pedidoId === "") {
    alert("Debes ingresar un ID válido.");
  }
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

async function askForPedidoAndExecute(method, path, requiresBody = false) {
  const id = prompt("Ingresa el ID del Pedido (pedido_id):");

  if (!id) return alert("⚠️ Debes ingresar un pedido_id válido.");
  if (!UUID_REGEX.test(id)) return alert("❌ Error ID invalido.");

  const finalPath = path.replace("{pedido_id}", id);
  const url = BASE + finalPath;

  if (requiresBody) {
    showBodyModal(finalPath, async body => await callAuth(url, method, body));
  } else {
    await callAuth(url, method);
  }
}

function createAsignarProveedorBody() {
  const today = new Date();
  const twoDaysLater = new Date();
  twoDaysLater.setDate(today.getDate() + 2);

  const formatDate = (date) => date.toISOString().slice(0, 16);

  let proveedorOptions = '';
  EXAMPLE_PROVEEDORES.forEach(prov => {
    proveedorOptions += `<option value="${prov.id}">${prov.nombre} (${prov.id.substring(0, 8)}...)</option>`;
  });

  return `
    <div class="mb-3">
      <label for="proveedor_id_select" class="form-label">Proveedor a Asignar</label>
      <select id="proveedor_id_select" class="form-select">
        ${proveedorOptions}
      </select>
    </div>

    <div class="mb-3">
      <label for="fecha_inicio_input" class="form-label">Fecha Inicio (YYYY-MM-DDTHH:MM)</label>
      <input type="datetime-local" class="form-control"
      id="fecha_inicio_input" value="${formatDate(today)}">
    </div>

    <div class="mb-3">
      <label for="fecha_fin_input" class="form-label">Fecha Fin (YYYY-MM-DDTHH:MM)</label>
      <input type="datetime-local" class="form-control"
      id="fecha_fin_input" value="${formatDate(twoDaysLater)}">
    </div>

    <div class="mb-3">
      <label for="correlation_id_input" class="form-label">Correlation ID</label>
      <input type="text" class="form-control" id="correlation_id_input" value="HOLD2">
    </div>
  `;
}




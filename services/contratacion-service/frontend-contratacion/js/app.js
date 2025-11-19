// ===== CONFIG =====
const BASE = "http://127.0.0.1:8040";  
const OPENAPI_URL = `${BASE}/openapi.json`;

const EXAMPLE_PAQUETES = {
   
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb": "PKG-LOCAL-01: Paquete Local Premium (S/24000)",
    "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa": "PKG-MUSICA-01: Paquete Música Premium (S/10800)",
    "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0": "PKG-PREMIUM-100: Premium 100 pax (S/12300)",
};

let lastSearchedPedidoId = null; 


// ===== TOKEN STORAGE =====
  function getStorageKey() {
    
    if (window.location.pathname.includes('admin.html')) {
      return "token_contratacion_admin";
    }
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


async function callAuth(url, method = "GET", body = null) {
  const headers = { "Accept": "application/json" };
  if (getToken()) headers["Authorization"] = `Bearer ${getToken()}`;
  if (body) headers["Content-Type"] = "application/json";

  try { 
    const response = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined });
    const text = await response.text();
    
    // Mostrar en el nuevo modal de respuesta
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
  // Excluir endpoints 
  if (path.includes("/contratacion/v1/contratacion/admin/")) continue;
  if (path.includes("/contratacion/v1/contratacion/pedidos/{pedido_id}/enviar-resumen")) continue;    
  if (path.includes("/contratacion/_debug/")) continue;  
  if (path.includes("/contratacion/health")) continue;      
  // Ruta de cliente
  for (const method in openapi.paths[path]) {
    endpoints.push({
      method: method.toUpperCase(),
      path,
      summary: openapi.paths[path][method].summary || "",
      isAdmin: false,   
      secured: !!openapi.paths[path][method].security
    });
  }
}

    container.innerHTML = "";
    endpoints.forEach(ep => renderEndpoint(ep, role));

  } catch (err) {
    container.innerHTML = `<div class="col-12 text-danger">❌ Error cargando OpenAPI: ${err.message}</div>`;
  }
}

function renderEndpoint(ep, role) {
  const container = document.getElementById("endpoints");

  const color = ep.method === "GET" ? "m-get"
    : ep.method === "POST" ? "m-post"
    : ep.method === "DELETE" ? "m-delete"
    : "m-patch";

  const disabled = ep.isAdmin && role !== "admin" ? "opacity-50 pointer-events-none" : "";
  const badge = ep.isAdmin ? `<span class="badge bg-danger ms-2">ADMIN</span>` : "";

let displayTitle = ep.summary || ep.path; 

  if (ep.path === "/contratacion/v1/contratacion/pedidos") {
    displayTitle = "Crear Pedido"; 
  } else if (ep.path === "/contratacion/v1/contratacion/pedidos/mios") {
    displayTitle = "Pedidos"; 
  } else if (ep.path.includes("/contratacion/v1/contratacion/pedidos/{pedido_id}")) {
    displayTitle = "Consultar Detalle de Pedidos"; 
  }

let buttonText = "Try It";  

if (ep.method === "GET" && ep.path === "/contratacion/health") {
  buttonText = "Ver Estado del Sistema";
}
if (ep.method === "POST" && ep.path === "/contratacion/v1/contratacion/pedidos") {
  buttonText = "Crear Pedido";
}
if (ep.method === "GET" && ep.path === "/contratacion/v1/contratacion/pedidos/mios") {
  buttonText = "Ver Mis Pedidos";
}
// Botón ID
if (ep.path === "/contratacion/v1/contratacion/pedidos/{pedido_id}") {
  buttonText = "Ver Detalle";
  buttonHTML = `<button class="btn btn-outline-success btn-sm" onclick="showDynamicIdModal('${ep.method}', '${ep.path}')">${buttonText}</button>`;
} else {
 
  buttonHTML = `<button class="btn btn-outline-primary btn-sm" onclick="tryEndpoint('${ep.method}', '${ep.path}')">${buttonText}</button>`;
}


  container.insertAdjacentHTML("beforeend", `
<div class="col-12">
  <div class="card p-3 card-endpoint ${disabled}">
    <div class="d-flex justify-content-between">
      <div>
        <span class="method-badge ${color}">${ep.method}</span>
        <span class="ms-2 fw-bold">${displayTitle}</span>
        ${badge}
        
      </div>
     ${buttonHTML}
    </div>
  </div>
</div>`);
}
// ===== TRY ENDPOINT =====
async function tryEndpoint(method, path) {
  const url = BASE + path;

  if (["POST", "PATCH", "PUT"].includes(method)) {
    
    showBodyModal(async body => await callAuth(url, method, body), path); 
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

function showBodyModal(callback, path) { 
  const modal = new bootstrap.Modal(document.getElementById("bodyModal"));
  const formContainer = document.getElementById("body-form-container");
  const jsonEditor = document.getElementById("body-json");
  const btnToggle = document.getElementById("btn-toggle-json");

  // Limpiar el textarea por defecto
  jsonEditor.value = "";
  jsonEditor.style.display = 'none';
  btnToggle.innerText = "Mostrar Editor JSON";


  btnToggle.onclick = () => {
      const isVisible = jsonEditor.style.display !== 'none';
      jsonEditor.style.display = isVisible ? 'none' : 'block';
      btnToggle.innerText = isVisible ? "Mostrar Editor JSON" : "Ocultar Editor JSON";
  };
  
  //  FORMULARIO DE CREACIÓN DE PEDIDO
  if (path === "/contratacion/v1/contratacion/pedidos") {
      
      formContainer.innerHTML = createPedidoFormHTML(); 
      formContainer.style.display = 'block';
      document.querySelector("#bodyModal .modal-title").textContent = "Crear Nuevo Pedido";
  } else {
   
      formContainer.innerHTML = '';
      formContainer.style.display = 'none';
      jsonEditor.style.display = 'block'; 
      document.querySelector("#bodyModal .modal-title").textContent = "Enviar JSON Body";
  }

  modal.show();

  
  document.getElementById("btn-send-body").onclick = async () => {
    let raw = "";
    let sequenceNumber = null; 
    
   
    if (path === "/contratacion/v1/contratacion/pedidos") {
        const result = buildJsonFromForm(); 
        raw = result.jsonString;
        sequenceNumber = result.sequenceNumber; 
    } else {
       
        raw = jsonEditor.value.trim();
    }
    
    try {
      const json = raw ? JSON.parse(raw) : {};
      modal.hide();
      
      // La llamada real al API
      await callback(json);
      
     
      if (sequenceNumber !== null) {
          localStorage.setItem('lastRequestIdNumber', sequenceNumber);
      }
      
    } catch (e) {
      alert(`❌ JSON inválido: ${e.message}. Revisa los datos.`);
    }
  };
}

//  MODAL DE RESPUESTA 
function showResponseModal(content, status) {
  const modalElement = document.getElementById("responseModal");
  const modal = new bootstrap.Modal(modalElement);
  
  document.getElementById("response-content").innerText = content;
  
  const titleElement = document.querySelector("#responseModal .modal-title");
  titleElement.innerHTML = status 
    ? `Respuesta de la API (${status})` 
    : `Respuesta de la API`;

  
  const footer = document.querySelector("#responseModal .modal-footer");
  if (footer) {
    footer.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>`;
  }

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
  
  
  if (["POST", "PATCH", "PUT"].includes(method)) {
  
    const pedidoId = prompt(`Por favor, ingresa el ID del Pedido para: ${path}`);
    if (pedidoId) {

      const finalPath = path.replace(idParam, pedidoId);
      const url = BASE + finalPath;
      showBodyModal(finalPath, async body => await callAuth(url, method, body));
    } else if (pedidoId === "") {
      alert("Debes ingresar un ID válido.");
    }
    return;
  }

  // === FLUJO para GET de pedidos (Ver Detalle) 
  
  if (lastSearchedPedidoId) {
    const responseModalElement = document.getElementById("responseModal");
    const modal = new bootstrap.Modal(responseModalElement);
    modal.show();
    // Configuramos la barra de búsqueda en el modal con el último ID
    setupDetailSearch(method, path, lastSearchedPedidoId);
    return; 
  }
  
  // Si se ingresa la primera vez el id de pedido
  const pedidoId = prompt(`Por favor, ingresa el ID del Pedido (GET): ${path}`);

  if (pedidoId) {
 
    await fetchPedidoDetail(method, path, pedidoId);
  } else if (pedidoId === "") {
    alert("Debes ingresar un ID válido.");
  }
}

async function fetchPedidoDetail(method, pathTemplate, pedidoId) {
  if (!pedidoId) {
    alert("Debe ingresar un ID de Pedido.");
    return;
  }

  const finalPath = pathTemplate.replace("{pedido_id}", pedidoId);
  const url = BASE + finalPath;
  
  
  lastSearchedPedidoId = pedidoId; 

  //Llama a la API (llama internamente a showResponseModal)
  await callAuth(url, method);
  
 
  setupDetailSearch(method, pathTemplate, pedidoId);
}

// FUNCIÓN  DE BARRA DE BÚSQUEDA
function setupDetailSearch(method, path, currentId) {
  const footerElement = document.querySelector("#responseModal .modal-footer");
   
  if (!footerElement) return;
  
  //  barra de búsqueda persistente
  footerElement.innerHTML = `
    <div class="input-group">
      <input type="text" id="new-pedido-id" class="form-control" 
          placeholder="ID actual: ${currentId} | Nuevo ID de Pedido" value="${currentId}">
      <button class="btn btn-warning" type="button" id="btn-search-new-id">
        Buscar Nuevo Detalle
      </button>
    </div>
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
  `;
  
  // botón de búsqueda
  document.getElementById("btn-search-new-id").onclick = async () => {
    const newId = document.getElementById("new-pedido-id").value.trim();
    if (newId) {
      // Llamamos a fetchPedidoDetail con el nuevo ID.
      await fetchPedidoDetail(method, path, newId);
    } else {
      alert("Ingresa un ID de Pedido válido para buscar.");
    }
  };
}

function createPedidoFormHTML() {
    
    let lastRequestIdNumber = parseInt(localStorage.getItem('lastRequestIdNumber') || '1');
    const nextRequestIdNumber = (lastRequestIdNumber + 1).toString().padStart(3, '0');
    const nextRequestId = `PEDIDO_NOVIEMBRE_${nextRequestIdNumber}`;
    
    // Lógica de  Paquetes
    const paqueteOptions = Object.entries(EXAMPLE_PAQUETES).map(([id, name]) => {
        
        const selected = id === 'bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0' ? 'selected' : '';
        return `<option value="${id}" ${selected}>${name} (${id.substring(0, 8)}...)</option>`;
    }).join(''); 

    //plantilla para selector  de paquetes
    return `
        <form id="pedido-form" class="row g-3">
            <h6 class="mt-0">Datos del Pedido</h6>
            
            <div class="col-md-6">
                <label for="form-cliente_id" class="form-label">Cliente ID (UUID)</label>
                <input type="text" class="form-control" id="form-cliente_id" required 
                       value="1e45e1a8-bf0c-11f0-b7b8-089798e03433">
            </div>
            
            <div class="col-md-6">
                <label for="form-paquete_id" class="form-label">Paquete (Selecciona el ID)</label>
                <select class="form-select" id="form-paquete_id" required>
                    ${paqueteOptions} 
                </select>
            </div>
            
            <div class="col-12">
                <label for="form-request_id" class="form-label">Request ID (Referencia)</label>
                <input type="text" class="form-control" id="form-request_id" required 
                       value="${nextRequestId}"> 
                <small class="text-muted">ID Sugerido. Se incrementa automáticamente.</small>
            </div>
            
            <h6 class="mt-4">Detalles del Evento</h6>
            
            <div class="col-md-4">
                <label for="form-fecha_evento" class="form-label">Fecha Evento</label>
                <input type="date" class="form-control" id="form-fecha_evento" required 
                       value="2025-11-11">
            </div>
            <div class="col-md-4">
                <label for="form-hora_inicio" class="form-label">Hora Inicio</label>
                <input type="time" class="form-control" id="form-hora_inicio" required 
                       value="18:00:00">
            </div>
            <div class="col-md-4">
                <label for="form-hora_fin" class="form-label">Hora Fin</label>
                <input type="time" class="form-control" id="form-hora_fin" required 
                       value="20:00:00">
            </div>
            <div class="col-12">
                <label for="form-ubicacion" class="form-label">Ubicación</label>
                <input type="text" class="form-control" id="form-ubicacion" required 
                       value="Av. Los Olivos 123, Lima">
            </div>
        </form>
    `;
}

function buildJsonFromForm() {
    // Lee los valores de los inputs y construye el objeto JSON
    const data = {
        cliente_id: document.getElementById('form-cliente_id').value,
        paquete_id: document.getElementById('form-paquete_id').value,
        request_id: document.getElementById('form-request_id').value,
        fecha_evento: document.getElementById('form-fecha_evento').value,
        hora_inicio: document.getElementById('form-hora_inicio').value,
        hora_fin: document.getElementById('form-hora_fin').value,
        ubicacion: document.getElementById('form-ubicacion').value
    };
    
   // Extraer el número de secuencia para guardarlo 
    const match = data.request_id.match(/_(\d+)$/);
    const sequenceNumber = match ? parseInt(match[1], 10) : null;

    return {
        jsonString: JSON.stringify(data),
        sequenceNumber: sequenceNumber
    };
} 
// js/api.js
// ==========================================
// Cliente ligero para el servicio IAM (fetch)
// ==========================================

// --- Base URL (se puede sobreescribir con window.API_BASE) ---
const RAW_BASE = (typeof window !== "undefined" && window.API_BASE)
  ? window.API_BASE
  : "http://127.0.0.1:8010/iam";

// Normaliza para evitar // al concatenar paths
function normalizeBase(base) {
  return String(base || "").replace(/\/+$/, "");
}
export const API_BASE = normalizeBase(RAW_BASE);

// --- Base URL catálogo (se puede sobreescribir con window.CATALOGO_API_BASE) ---
const RAW_CATALOGO_BASE = (typeof window !== "undefined" && window.CATALOGO_API_BASE)
  ? window.CATALOGO_API_BASE
  : "http://127.0.0.1:8020/catalogo";

export const CATALOGO_API_BASE = normalizeBase(RAW_CATALOGO_BASE);

// --- Configuración global ---
const DEFAULT_TIMEOUT_MS = 12_000;

// --- Estado de autenticación (solo token JWT) ---
let _token = null;

/** Establece o limpia el token JWT para los requests. */
export function setToken(t) { _token = t || null; }
/** Obtiene el token actual (por si quieres leerlo en otros módulos). */
export function getToken() { return _token; }

// --- Utilidades internas ---

/** Construye querystring a partir de un objeto (ignora null/undefined). */
function qs(params = {}) {
  const entries = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null);
  if (!entries.length) return "";
  const s = entries
    .map(([k, v]) =>
      `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join("&");
  return `?${s}`;
}

/** Intenta parsear JSON solo si el contenido y el tamaño lo ameritan. */
async function safeJson(res) {
  const ct = res.headers.get("content-type") || "";
  if (!res.body) return null;
  if (res.status === 204) return null;
  if (ct.includes("application/json")) {
    try { return await res.json(); }
    catch { /* cae abajo y devuelve texto */ }
  }
  // Fallback a texto
  try { return await res.text(); } catch { return null; }
}

/** Crea un error enriquecido con contexto del request/response. */
function toHttpError({ res, body, url, method }) {
  const err = new Error(
    (typeof body === "string" && body) ||
    (body && body.detail) ||
    res.statusText ||
    `HTTP ${res.status}`
  );
  err.name = "HttpError";
  err.status = res.status;
  err.data = body;
  err.url = url;
  err.method = method;
  return err;
}

/** Lanza un error específico para 401/403 con nombre diferenciable. */
function throwIfAuthError(err) {
  if (err && (err.status === 401 || err.status === 403)) {
    const e = new Error(err.message || "No autorizado");
    e.name = "AuthError";
    e.status = err.status;
    e.data = err.data;
    e.url = err.url;
    e.method = err.method;
    throw e;
  }
  throw err;
}

/** Timeout con AbortController. */
function withTimeout(ms = DEFAULT_TIMEOUT_MS) {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(new DOMException("timeout", "TimeoutError")), ms);
  return { signal: ctrl.signal, clear: () => clearTimeout(id) };
}

// --- Core HTTP (exportado por si lo necesitas en otros módulos) ---
export async function http(method, path, body, { timeoutMs } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (_token) headers["Authorization"] = `Bearer ${_token}`;

  const url = `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
  const { signal, clear } = withTimeout(timeoutMs ?? DEFAULT_TIMEOUT_MS);

  let res;
  try {
    console.log(`🌐 HTTP ${method} ${url}`, body ? { body } : '');
    res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (err) {
    clear();
    // Diferencia net::ERR_FAILED / abort / timeout
    if (err?.name === "AbortError" || err?.name === "TimeoutError") {
      const e = new Error("Solicitud expirada");
      e.name = "TimeoutError";
      e.url = url;
      e.method = method;
      throw e;
    }
    const e = new Error("Fallo de red o CORS");
    e.name = "NetworkError";
    e.cause = err;
    e.url = url;
    e.method = method;
    throw e;
  } finally {
    clear();
  }

  // Parse response & normalize errors like httpCatalogo does
  const parsed = await safeJson(res);

  if (!res.ok) {
    console.error(`❌ HTTP ${res.status} ${method} ${url}`, parsed);
    throwIfAuthError(toHttpError({ res, body: parsed, url, method }));
  }
  
  console.log(`✅ HTTP ${res.status} ${method} ${url}`, parsed);
  return parsed;
}

async function httpCatalogo(method, path, body, { timeoutMs } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (_token) headers["Authorization"] = `Bearer ${_token}`;

  const url = `${CATALOGO_API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
  const { signal, clear } = withTimeout(timeoutMs ?? DEFAULT_TIMEOUT_MS);

  let res;
  try {
    res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (err) {
    clear();
    // Diferencia net::ERR_FAILED / abort / timeout
    if (err?.name === "AbortError" || err?.name === "TimeoutError") {
      const e = new Error("Solicitud expirada");
      e.name = "TimeoutError";
      e.url = url;
      e.method = method;
      throw e;
    }
    const e = new Error("Fallo de red o CORS");
    e.name = "NetworkError";
    e.cause = err;
    e.url = url;
    e.method = method;
    throw e;
  } finally {
    clear();
  }

  const parsed = await safeJson(res);

  if (!res.ok) {
    throwIfAuthError(toHttpError({ res, body: parsed, url, method }));
  }
  return parsed;
}

// ==========================================
//          Endpoints del servicio IAM
// ==========================================
export const IAM = {
  // ---------- Públicas ----------
  /**
   * Autenticación de usuario.
   * @returns {Promise<{ access_token:string, token_type:string, expires_in:number, user?:any }>}
   */
  login: (email, password) =>
    http("POST", "/auth/login", { email, password }),

  /**
   * Registro público de usuario.
   */
  register: (email, password, nombre = "", telefono = "") =>
    http("POST", "/auth/register", { email, password, nombre, telefono }),

  /** Salud del servicio. */
  health: () => http("GET", "/health"),

  // ---------- Protegidas ----------
  /** Información del usuario autenticado. */
  me: () => http("GET", "/me"),

  // ---------- Admin ----------
  /**
   * Lista de usuarios con paginación y filtros sencillos (email).
   * Devuelve `data.items` o un array simple (según backend).
   */
  adminUsers: (limit = 20, offset = 0, email = undefined) =>
    http("GET", `/admin/users${qs({ limit, offset, email })}`),

  /**
   * Crea usuario (ADMIN).
   * @param {{email:string, password:string, role?:string, nombre?:string, telefono?:string}} user
   */
  adminCreateUser: (user) =>
    http("POST", "/admin/users", user),

  /** Obtiene un usuario por ID (ADMIN). */
  adminGetUser: (id) =>
    http("GET", `/admin/users/${encodeURIComponent(id)}`),

  /** Actualización parcial (ADMIN) - VERSIÓN MEJORADA */
  /** Actualización parcial (ADMIN) - CON DEBUG MEJORADO */
  adminPatchUser: async (id, patch) => {
      console.log("🔧 adminPatchUser llamado:", { id, patch });
      
      // DEBUG: Mostrar headers y payload completo
      const token = getToken();
      console.log("🔑 Token presente:", !!token);
      console.log("📦 Payload completo a enviar:", JSON.stringify(patch, null, 2));
      
      try {
          const response = await http("PATCH", `/admin/users/${encodeURIComponent(id)}`, patch);
          console.log("✅ Respuesta de adminPatchUser:", response);
          return response;
      } catch (error) {
          console.error("❌ Error en adminPatchUser:", {
              status: error.status,
              message: error.message,
              data: error.data
          });
          throw error;
      }
  },

  /** Elimina un usuario (ADMIN). */
  adminDeleteUser: (id) =>
    http("DELETE", `/admin/users/${encodeURIComponent(id)}`),
};

// ==========================================
//       Endpoints del servicio Catálogo
// ==========================================
export const CATALOGO = {
  /** Salud del servicio de catálogo. */
  health: () => httpCatalogo("GET", "/health"),

  /**
   * Lista de tipos de eventos/servicios disponibles.
   * @param {Object} [params]  Opcional: filtros adicionales.
   */
  tipos: (params = {}) =>
    httpCatalogo("GET", `/v1/catalogo/tipos${qs(params)}`),

  /**
   * Lista de servicios del catálogo.
   * @param {Object} [params]  Ej: { tipo_id, activo }
   */
  servicios: (params = {}) =>
    httpCatalogo("GET", `/v1/catalogo/servicios${qs(params)}`),

  /**
   * Opciones o características configurables de los servicios.
   */
  opciones: (params = {}) =>
    httpCatalogo("GET", `/v1/catalogo/opciones${qs(params)}`),

  /**
   * Paquetes disponibles (bundle de servicios/opciones).
   */
  paquetes: (params = {}) =>
    httpCatalogo("GET", `/v1/catalogo/paquetes${qs(params)}`),

  /**
   * Detalle de un paquete específico por ID.
   */
  paquetePorId: (id) =>
    httpCatalogo("GET", `/v1/catalogo/paquetes/${encodeURIComponent(id)}`),
};

// ==========================================
// Export opcional de utilidades (por si las usas)
// ==========================================
export const utils = { qs, safeJson };
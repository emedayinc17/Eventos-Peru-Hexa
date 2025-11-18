// js/services.js
// Clientes ligeros para Proveedores y Contratación
import { getToken } from "./api.js";

function normalizeBase(base) { return String(base || "").replace(/\/+$/, ""); }

const RAW_PROVEEDORES_BASE = (typeof window !== "undefined" && window.PROVEEDORES_API_BASE)
  ? window.PROVEEDORES_API_BASE
  : "http://127.0.0.1:8030/proveedores";
const PROVEEDORES_BASE = normalizeBase(RAW_PROVEEDORES_BASE);

const RAW_CONTRATACION_BASE = (typeof window !== "undefined" && window.CONTRATACION_API_BASE)
  ? window.CONTRATACION_API_BASE
  : "http://127.0.0.1:8040/contratacion";
const CONTRATACION_BASE = normalizeBase(RAW_CONTRATACION_BASE);

async function fetchJson(base, method, path, body) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken && getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const url = `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });
  if (!res.ok) {
    const txt = await res.text().catch(()=>null);
    const json = txt && txt.startsWith("{") ? JSON.parse(txt) : txt;
    const err = new Error((json && json.detail) || res.statusText || `HTTP ${res.status}`);
    err.status = res.status;
    err.data = json;
    throw err;
  }
  if (res.status === 204) return null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

export const PROVEEDORES = {
  health: () => fetchJson(PROVEEDORES_BASE, "GET", "/health"),
  buscar: (servicio_id, fecha, limit = 50, offset = 0) =>
    fetchJson(PROVEEDORES_BASE, "GET", `/v1/proveedores${servicio_id?`?servicio_id=${encodeURIComponent(servicio_id)}&fecha=${encodeURIComponent(fecha)}&limit=${limit}&offset=${offset}`:`?fecha=${encodeURIComponent(fecha)}&limit=${limit}&offset=${offset}`}`),
  crearReserva: (payload) => fetchJson(PROVEEDORES_BASE, "POST", "/v1/proveedores/reservas", payload),
  liberarReserva: (id) => fetchJson(PROVEEDORES_BASE, "DELETE", `/v1/proveedores/reservas/${encodeURIComponent(id)}`),
};

export const CONTRATACION = {
  health: () => fetchJson(CONTRATACION_BASE, "GET", "/health"),
  crearPedido: (body) => fetchJson(CONTRATACION_BASE, "POST", "/v1/contratacion/pedidos", body),
  misPedidos: () => fetchJson(CONTRATACION_BASE, "GET", "/v1/contratacion/pedidos/mios"),
  detallePedido: (id) => fetchJson(CONTRATACION_BASE, "GET", `/v1/contratacion/pedidos/${encodeURIComponent(id)}`),
  enviarResumen: (id, body) => fetchJson(CONTRATACION_BASE, "POST", `/v1/contratacion/pedidos/${encodeURIComponent(id)}/enviar-resumen`, body),
};

// js/healthcheck.js
// Utilidad para verificar salud de los servicios desde el frontend (modo local)
import { IAM, CATALOGO } from "./api.js";
import { PROVEEDORES, CONTRATACION } from "./services.js";

// Realiza una petición de salud y mide tiempo. Devuelve { name, ok, status, timeMs, body }
async function check(name, fn) {
  const start = performance.now();
  try {
    const body = await fn();
    const timeMs = Math.round(performance.now() - start);
    return { name, ok: true, status: 200, timeMs, body };
  } catch (err) {
    const timeMs = Math.round(performance.now() - start);
    const status = err && err.status ? err.status : null;
    return { name, ok: false, status, timeMs, error: (err && err.message) || String(err) };
  }
}

export async function verifyAllServices({ timeoutMs = 5000 } = {}) {
  // Ejecutar checks en paralelo
  const checks = [
    check("IAM", () => IAM.health()),
    check("CATALOGO", () => CATALOGO.health()),
    check("PROVEEDORES", () => PROVEEDORES.health()),
    check("CONTRATACION", () => CONTRATACION.health()),
  ];

  const results = await Promise.all(checks);
  return results;
}

export function resultsToHtml(results) {
  const rows = results.map(r => {
    const statusBadge = r.ok ? `<span class="badge bg-success">OK</span>` : `<span class="badge bg-danger">ERR</span>`;
    const info = r.ok ? `status: ${r.status}` : `status: ${r.status || '-'} error: ${escapeHtml(r.error || '')}`;
    return `<tr>
      <td>${escapeHtml(r.name)}</td>
      <td>${statusBadge}</td>
      <td>${escapeHtml(String(r.timeMs))} ms</td>
      <td><small class="text-muted">${escapeHtml(info)}</small></td>
    </tr>`;
  }).join('');

  return `
    <div class="table-responsive">
      <table class="table table-sm align-middle">
        <thead><tr><th>Servicio</th><th>OK</th><th>Latencia</th><th>Info</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export default { verifyAllServices, resultsToHtml };

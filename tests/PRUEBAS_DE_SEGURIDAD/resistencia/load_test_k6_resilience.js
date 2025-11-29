import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 50,
  duration: '20s',
};

const API_BASE = __ENV.API_BASE || 'http://localhost:8000';

export default function () {
  // Golpear endpoints críticos para medir latencia y errores
  const r1 = http.get(`${API_BASE}/api/iam/health`);
  const r2 = http.get(`${API_BASE}/api/catalogo/health`);
  check(r1, { 'iam ok': r => r.status === 200 });
  check(r2, { 'catalog ok': r => r.status === 200 });
  sleep(1);
}

import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

const API_BASE = __ENV.API_BASE || 'http://localhost:8000';

export default function () {
  const url = `${API_BASE}/api/contratacion/pedidos`;
  const payload = JSON.stringify({
    tipo_evento_id: '11111111-1111-1111-1111-111111111111',
    fecha_evento: '2026-01-01',
    num_personas: 20,
  });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post(url, payload, params);
  check(res, { 'status is 2xx': r => r.status >= 200 && r.status < 300 });
  sleep(1);
}

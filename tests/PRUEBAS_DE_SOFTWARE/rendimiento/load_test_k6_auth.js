import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 5 },
    { duration: '20s', target: 10 },
    { duration: '10s', target: 0 },
  ],
};

const API_BASE = __ENV.API_BASE || 'http://localhost:8000';

function login() {
  const payload = JSON.stringify({ email: 'cliente@test.com', password: 'Cliente123!' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const r = http.post(`${API_BASE}/api/iam/login`, payload, params);
  if (r.status === 200) {
    try {
      return r.json().access_token;
    } catch (e) {
      return null;
    }
  }
  return null;
}

export default function () {
  const token = login();
  if (!token) {
    return;
  }
  const headers = { headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` } };
  const payload = JSON.stringify({ tipo_evento_id: '11111111-1111-1111-1111-111111111111', fecha_evento: '2026-02-01', num_personas: 15 });
  const res = http.post(`${API_BASE}/api/contratacion/pedidos`, payload, headers);
  check(res, { 'status is 2xx': r => r.status >= 200 && r.status < 300 });
  sleep(1);
}

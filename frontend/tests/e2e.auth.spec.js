import { test, expect } from '@playwright/test';
import fs from 'fs';

const BASE = process.env.FRONTEND_URL || 'http://localhost:5173';
const GATEWAY = process.env.GATEWAY_URL || 'http://localhost:8000';

// Credenciales de prueba (seeded)
const TEST_EMAIL = process.env.TEST_EMAIL || 'gateway_test@test.com';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test123';

test.describe('Autenticación y flujo cliente (UI)', () => {
  test('Login via API + visitar Create Order Wizard', async ({ page, request }) => {
    const logs = [];
    page.on('console', m => logs.push(`${m.type()}: ${m.text()}`));
    page.on('requestfailed', (req) => {
      const failure = req.failure();
      logs.push(`REQ_FAILED: ${req.url()} status=${req.response()?.status() || 'N/A'} failure=${failure?.errorText || ''}`);
    });
    // 1) Login via API (gateway -> iam)
    const loginResp = await request.post(`${GATEWAY}/api/iam/auth/login`, {
      data: { email: TEST_EMAIL, password: TEST_PASSWORD }
    });
    expect(loginResp.ok()).toBeTruthy();
    const loginBody = await loginResp.json();
    expect(loginBody.access_token).toBeTruthy();
    const token = loginBody.access_token;

    // 2) Obtener perfil /iam/me usando token
    const meResp = await request.get(`${GATEWAY}/api/iam/me`, { headers: { Authorization: `Bearer ${token}` } });
    expect(meResp.ok()).toBeTruthy();
    const user = await meResp.json();

    // 3) Inyectar token y user en localStorage antes de cargar la app
    await page.context().addInitScript((t, u) => {
      window.localStorage.setItem('access_token', t);
      window.localStorage.setItem('user', JSON.stringify(u));
    }, token, user);

    // 4) Ir a la página protegida y verificar contenido
    try {
      await page.goto(`${BASE}/cliente/pedido/nuevo`, { waitUntil: 'networkidle' });
      // Espera a que el wizard cargue
      await expect(page.locator('text=Crear Nuevo Pedido')).toBeVisible({ timeout: 20000 });

      // También verificar que el botón Siguiente esté presente
      await expect(page.locator('text=Siguiente →')).toBeVisible();
    } catch (err) {
      // Guardar evidencia para debugging
      await page.screenshot({ path: 'playwright-failure-create-order.png', fullPage: true });
      const html = await page.content();
      fs.writeFileSync('playwright-failure-create-order.html', html, 'utf8');
      fs.writeFileSync('playwright-failure-console.log', logs.join('\n'), 'utf8');
      throw err;
    }
  });
});

import { test, expect } from '@playwright/test';

// Ajusta la URL base si tu Vite corre en otro puerto
const BASE = process.env.FRONTEND_URL || 'http://localhost:5173';

test.describe('Smoke UI tests', () => {
  test('Home carga y título correcto', async ({ page }) => {
    const resp = await page.goto(BASE, { waitUntil: 'networkidle' });
    // Verificamos que el HTML se sirvió correctamente y el título básico
    expect(resp && resp.ok()).toBeTruthy();
    await expect(page).toHaveTitle(/frontend/);
  });
});

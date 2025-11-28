const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  timeout: 60_000,
  use: {
    headless: true,
    ignoreHTTPSErrors: true,
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } }
  ],
  testDir: 'tests'
});

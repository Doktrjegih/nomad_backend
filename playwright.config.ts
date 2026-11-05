import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './pwa-tests', testMatch: '**/*.spec.ts', fullyParallel: false,
  use: { baseURL: 'http://127.0.0.1:4173', headless: true, launchOptions: { executablePath: process.env.CHROMIUM_PATH ?? '/usr/bin/chromium', args: ['--no-sandbox'] } },
  webServer: { command: 'npm run preview -- --port 4173 --strictPort', url: 'http://127.0.0.1:4173', reuseExistingServer: false },
});

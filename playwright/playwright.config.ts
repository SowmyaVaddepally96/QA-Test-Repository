import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  retries: 1,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? 'dot' : 'list',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'smoke', testMatch: /.*smoke.*\.spec\.ts/ },
    { name: 'regression', testMatch: /.*regression.*\.spec\.ts/ },
    { name: 'auth', testMatch: /.*auth.*\.spec\.ts/ },
  ],
});

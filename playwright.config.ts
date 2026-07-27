import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8099',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'python run_live_test.py',
    port: 8099,
    reuseExistingPort: !process.env.CI,
    timeout: 120 * 1000,
  },
  expect: {
    timeout: 10000,
  },
});
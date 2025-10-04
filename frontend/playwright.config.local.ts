import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for local testing with existing servers
 * Use this when dev/backend servers are already running
 */
export default defineConfig({
  testDir: './tests',

  /* Run tests in files in parallel */
  fullyParallel: false, // Sequential for PDF tests
  workers: 1, // Single worker for stability

  /* Retry failed tests */
  retries: 1,

  /* Reporter to use */
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }]
  ],

  /* Shared settings for all the projects below */
  use: {
    /* Base URL - assumes dev server running on 3000 */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Video on failure */
    video: 'retain-on-failure',

    /* Longer action timeout for PDF generation */
    actionTimeout: 30 * 1000,

    /* Navigation timeout */
    navigationTimeout: 60 * 1000,
  },

  /* Global timeout for each test */
  timeout: 90 * 1000,

  /* Expect timeout */
  expect: {
    timeout: 10 * 1000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        /* Slower for PDF generation */
        slowMo: 500,
      },
    },
  ],

  /* NO webServer - use existing dev server */
  // webServer: undefined,
});

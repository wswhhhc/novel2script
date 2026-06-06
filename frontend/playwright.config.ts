import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://127.0.0.1:15173",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "python -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 18000",
      url: "http://127.0.0.1:18000/health",
      reuseExistingServer: false,
      env: {
        ENABLE_AI_GENERATION: "false",
        ENABLE_GENERATION_CACHE: "false",
        MODEL_API_KEY: "",
        MODEL_NAME: "",
        NOVEL2SCRIPT_DB_PATH: "../backend/data/novel2script-e2e.db",
      },
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 15173",
      url: "http://127.0.0.1:15173",
      reuseExistingServer: false,
      env: {
        VITE_API_BASE_URL: "http://127.0.0.1:18000",
      },
    },
  ],
});

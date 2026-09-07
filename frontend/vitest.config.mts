import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Next.js 16 documents Vitest (not Jest) as the unit-testing setup — see
// node_modules/next/dist/docs/01-app/02-guides/testing/vitest.md. This
// covers unit tests only (schemas, presentational components); full page
// flows are still verified by hand in a real browser per phase, as noted
// in each README's "how this was verified" section.
export default defineConfig({
  resolve: { tsconfigPaths: true }, // resolves the "@/*" alias from tsconfig.json
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    exclude: ["node_modules/**", ".next/**"],
  },
});

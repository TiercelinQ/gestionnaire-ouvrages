import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Le plugin fournit la transformation JSX automatique : sans lui, les composants
  // de test échouent sur un React non défini.
  plugins: [react()],
  test: {
    environment: "jsdom",
    include: ["test/**/*.test.ts", "test/**/*.test.tsx"],
    setupFiles: ["./test/setup.ts"],
  },
});

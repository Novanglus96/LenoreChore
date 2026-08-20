import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    globals: true,
    environment: "happy-dom",
    // Polyfills Vuetify needs that happy-dom does not provide.
    setupFiles: ["./src/__tests__/setup.js"],
    // setup.js is support code, not a suite.
    exclude: ["**/node_modules/**", "**/dist/**", "**/__tests__/setup.js"],
    // Vuetify and vue-datepicker ship components that import their own .css.
    // Node cannot load those through the default externalised path
    // ("Unknown file extension .css"), so they have to be processed by Vite.
    server: {
      deps: {
        inline: ["vuetify", "@vuepic/vue-datepicker"],
      },
    },
  },
});

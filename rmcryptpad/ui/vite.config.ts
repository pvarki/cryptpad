import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { federation } from "@module-federation/vite";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: "/",
  build: {
    target: "chrome89",
    emptyOutDir: true,
    rollupOptions: {
      preserveEntrySignatures: "exports-only",
    },
  },
  plugins: [
    federation({
      filename: "remoteEntry.js",
      name: "cryptpad-integration",
      exposes: {
        "./remote-ui": "./src/App.tsx",
      },
      remotes: {},
      shared: {
        react: {
          requiredVersion: "^18.3.1",
          singleton: true,
        },
        "react-dom": {
          requiredVersion: "^18.3.1",
          singleton: true,
        },
      },
      runtime: "@module-federation/enhanced/runtime",
    }),
    react(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});

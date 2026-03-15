import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy REST API calls to the backend during development
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // Proxy WebSocket connections to the backend.
      // The configure callback suppresses ECONNABORTED errors caused by
      // React 18 StrictMode double-mount (first connection closes before
      // proxy finishes writing).
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (err) => {
            if ((err as NodeJS.ErrnoException).code === "ECONNABORTED") return;
            if (err.message?.includes("ECONNABORTED")) return;
            console.error("[ws proxy]", err.message);
          });
        },
      },
    },
  },
});

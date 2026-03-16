import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    watch: {
      // Reduce file-watcher load on Windows (chokidar + Defender interaction
      // can cause system-wide keyboard lag). See: vitejs/vite#4665
      usePolling: false,
      ignored: ["**/node_modules/**", "**/.git/**", "**/data/**"],
    },
    proxy: {
      // Proxy REST API calls to the backend during development
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      // Proxy WebSocket connections to the backend.
      // The configure callback suppresses ECONNABORTED errors caused by
      // React 18 StrictMode double-mount (first connection closes before
      // proxy finishes writing).
      "/ws": {
        target: "ws://127.0.0.1:8000",
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

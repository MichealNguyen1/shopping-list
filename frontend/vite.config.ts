import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy API calls trong dev để tránh CORS khi chạy local
    // Thay vì gọi http://localhost:8000/api trực tiếp,
    // gọi /api → Vite tự forward đến backend
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});

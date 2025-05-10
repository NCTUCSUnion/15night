import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  preview: {
    host: true,
    port: 4173,
    allowedHosts: ["15night.nctucsunion.me"],
  },
});

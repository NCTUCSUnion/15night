import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProd = mode === 'production'

  return {
    base: isProd ? '/admin/' : '/',
    plugins: [
      vue(),
      tailwindcss(),
    ],
    preview: {
      host: true,
      port: 4173,
      allowedHosts: ['15night.nctucsunion.me'],
    },
  }
})

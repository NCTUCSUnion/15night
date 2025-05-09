import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    // Required for history mode to work correctly during development
    historyApiFallback: true,
    proxy: {
      // Forward API requests to your backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

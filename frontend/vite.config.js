import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'https://github-activity-analyzer-0b0w.onrender.com', changeOrigin: true },
    },
  },
})

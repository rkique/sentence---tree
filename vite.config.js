import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['urchin-app-2-mzfse.ondigitalocean.app'],
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:5001',
        changeOrigin: true
      }
    },
    watch: {
      ignored: ['**/backend/**', '**/distances.csv', '**/instance/**', '**/__pycache__/**']
    }
  }
})
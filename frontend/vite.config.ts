import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/notes': 'http://localhost:8000',
      '/tags': 'http://localhost:8000',
      '/folders': 'http://localhost:8000',
      '/attachments': 'http://localhost:8000',
      '/search': 'http://localhost:8000',
      '/graph': 'http://localhost:8000',
      '/repos': 'http://localhost:8000'
    }
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Proxy para desarrollo local - redirige las peticiones a los microservicios
      '/api/iam': {
        target: 'http://localhost:8010',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/iam/, ''),
      },
      '/api/catalogo': {
        target: 'http://localhost:8020',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/catalogo/, ''),
      },
      '/api/proveedores': {
        target: 'http://localhost:8030',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/proveedores/, ''),
      },
      '/api/contratacion': {
        target: 'http://localhost:8040',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/contratacion/, ''),
      },
    },
  },
})

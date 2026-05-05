import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Default: dentro la rete Docker il backend si chiama "backend".
  // Per dev senza Docker setta VITE_DEV_PROXY_TARGET nel .env (es. l'URL Vercel di prod).
  const apiTarget = env.VITE_DEV_PROXY_TARGET || 'http://backend:8000'
  return {
    plugins: [vue()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': { target: apiTarget, changeOrigin: true, secure: true },
        '/media': { target: apiTarget, changeOrigin: true, secure: true },
      },
      allowedHosts: true,
    },
  }
})

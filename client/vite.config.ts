import react from '@vitejs/plugin-react'

/** @type {import('vite').UserConfig} */
export default {
  plugins: [react()],
  server: {
    proxy: {
      // remove this if you set VITE_API_BASE_URL in .env.local
      '/images': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
}

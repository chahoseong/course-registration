import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001/course-registration-711a4/asia-northeast3/fastapi_handler',
        changeOrigin: true,
      }
    }
  }
})

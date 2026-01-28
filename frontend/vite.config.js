import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0', // 允许外部访问
    port: 5173,
    watch: {
      usePolling: true, // 在Docker中需要polling模式
      interval: 1000
    },
    hmr: {
      host: 'localhost',
      port: 5173
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 监听所有网络接口，允许局域网访问
    port: 5173,
    // 配置代理，将 /hiagent、/health 和 /document 请求转发到本地后端
    proxy: {
      '/hiagent': {
        target: 'http://localhost:8888',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8888',
        changeOrigin: true,
      },
      '/document': {
        target: 'http://localhost:8888',
        changeOrigin: true,
      }
    }
  },
})

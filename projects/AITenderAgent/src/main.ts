import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// 配置 axios 默认值
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.headers.common['Content-Type'] = 'application/json'
axios.defaults.withCredentials = true

// 添加请求拦截器
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

interface RefreshResponse {
  token: string
}

// 添加响应拦截器
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // 如果是 401 错误且不是刷新 token 的请求
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // 尝试刷新 token
        const response = await axios.post<RefreshResponse>('/api/refresh')
        const newToken = response.data.token
        localStorage.setItem('token', newToken)
        
        // 更新原始请求的 token
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        
        // 重新发送原始请求
        return axios(originalRequest)
      } catch (refreshError) {
        // 如果刷新 token 失败，重定向到登录页面
        localStorage.removeItem('token')
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

app.use(createPinia())
app.use(ElementPlus)
app.use(router)

app.mount('#app')

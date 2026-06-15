import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000,  // 2 min — LLM calls can be slow
})

// Attach JWT token on every request
API.interceptors.request.use((config) => {
  try {
    const stored = localStorage.getItem('neuralchat_user')
    if (stored) {
      const user = JSON.parse(stored)
      if (user?.token) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${user.token}`
      }
    }
  } catch {
    localStorage.removeItem('neuralchat_user')
  }
  return config
})

// Auto-logout on 401
API.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('neuralchat_user')
    }
    return Promise.reject(error)
  }
)

export default API
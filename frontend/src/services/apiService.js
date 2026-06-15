import axios from 'axios'
import useAuthStore from '../store/authStore'

const DEFAULT_TIMEOUT = 120000
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
import { getStoredToken, clearStoredUser } from './authStorage'

function getToken() {
  return getStoredToken()
}

const api = axios.create({
  baseURL: BASE_URL,
  timeout: DEFAULT_TIMEOUT,
})

api.interceptors.request.use(
  (config) => {
    const token = getStoredToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      const networkError = new Error('Network error. Please check your connection.')
      networkError.status = null
      return Promise.reject(networkError)
    }

    const status = error.response.status
    let message = 'An unexpected error occurred.'

    if (status === 401) {
      clearStoredUser()
      useAuthStore.getState().logout()
      message = 'Session expired. Please sign in again.'
    } else if (status === 403) {
      message = 'You do not have permission to perform this action.'
    } else if (status === 404) {
      message = 'The requested resource was not found.'
    } else if (status >= 500) {
      message = 'Server error. Please try again later.'
    }

    if (error.response.data?.detail) {
      message = error.response.data.detail
    }

    const wrapped = new Error(message)
    wrapped.status = status
    wrapped.response = error.response
    return Promise.reject(wrapped)
  },
)

const apiService = {
  get(url, config) {
    return api.get(url, config)
  },
  post(url, data, config) {
    return api.post(url, data, config)
  },
  put(url, data, config) {
    return api.put(url, data, config)
  },
  delete(url, config) {
    return api.delete(url, config)
  },
  request(config) {
    return api.request(config)
  },
}

export default apiService

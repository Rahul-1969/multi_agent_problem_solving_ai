import apiService from './apiService'
import { LOGIN, REFRESH, REGISTER } from '../constants/apiEndpoints'

const STORAGE_KEY = 'neuralchat_user'

function getStoredUser() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

function saveUser(data) {
  // Store only non-sensitive profile data (tokens live in httpOnly cookies)
  const userdata = {
    username: data.username,
    name: data.name,
    email: data.email,
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(userdata))
  return userdata
}

async function login(usernameOrEmail, password) {
  const normalized = usernameOrEmail.trim().toLowerCase()
  const response = await apiService.post(LOGIN, { username: normalized, password })
  return saveUser(response.data)
}

async function refreshToken() {
  // Cookies send refresh_token automatically; body is optional
  const response = await apiService.post(REFRESH, {})
  return saveUser(response.data)
}

async function register(name, email, password) {
  const response = await apiService.post(REGISTER, { name, email, password })
  return response.data
}

async function logout() {
  try {
    await apiService.post('/auth/logout', {})
  } catch {
    // Best-effort: ignore errors if backend is unreachable
  }
  localStorage.removeItem(STORAGE_KEY)
}

export default {
  login,
  logout,
  refreshToken,
  getStoredUser,
  register,
  saveUser,
}

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

function saveStoredUser(data) {
  const userdata = {
    ...data,
    access_token: data.access_token,
    refresh_token: data.refresh_token,
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(userdata))
  return userdata
}

function getToken() {
  const user = getStoredUser()
  return user?.token || user?.access_token || null
}

function saveUser(data) {
  return saveStoredUser(data)
}

async function login(usernameOrEmail, password) {
  const normalized = usernameOrEmail.trim().toLowerCase()
  const response = await apiService.post(LOGIN, { username: normalized, password })
  return saveStoredUser(response.data)
}

async function refreshToken() {
  const user = getStoredUser()
  if (!user?.refresh_token) {
    throw new Error('No refresh token available.')
  }

  const response = await apiService.post(REFRESH, {
    refresh_token: user.refresh_token,
  })
  return saveStoredUser({ ...user, ...response.data })
}

async function register(name, email, password) {
  const response = await apiService.post(REGISTER, { name, email, password })
  return response.data
}

function logout() {
  localStorage.removeItem(STORAGE_KEY)
}

export default {
  login,
  logout,
  refreshToken,
  getToken,
  getStoredUser,
  register,
  saveUser,
}

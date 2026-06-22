const STORAGE_KEY = 'neuralchat_user'

export function getStoredUser() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export function saveStoredUser(data) {
  const userdata = { ...data }
  delete userdata.access_token
  delete userdata.refresh_token
  localStorage.setItem(STORAGE_KEY, JSON.stringify(userdata))
  return userdata
}

export function clearStoredUser() {
  localStorage.removeItem(STORAGE_KEY)
}



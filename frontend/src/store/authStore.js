import create from 'zustand'

const useAuthStore = create((set) => ({
  user: null,
  initializing: true,

  setUser(user) {
    set({ user })
  },

  setInitializing(initializing) {
    set({ initializing })
  },

  login(userData) {
    // Persist only non-sensitive profile data; tokens live in httpOnly cookies
    const safeData = {
      username: userData.username,
      name: userData.name,
      email: userData.email,
    }
    localStorage.setItem('neuralchat_user', JSON.stringify(safeData))
    set({ user: safeData })
  },

  logout() {
    localStorage.removeItem('neuralchat_user')
    set({ user: null })
  },

  async verifySession() {
    const stored = localStorage.getItem('neuralchat_user')
    if (!stored) {
      set({ user: null, initializing: false })
      return
    }

    try {
      const parsed = JSON.parse(stored)
      // Tokens are now httpOnly cookies; just verify user profile data exists
      if (!parsed?.username) {
        throw new Error('Invalid user data')
      }
      set({ user: parsed, initializing: false })
    } catch {
      localStorage.removeItem('neuralchat_user')
      set({ user: null, initializing: false })
    }
  },
}))

export default useAuthStore

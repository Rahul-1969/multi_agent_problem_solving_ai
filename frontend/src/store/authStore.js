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
    localStorage.setItem('neuralchat_user', JSON.stringify(userData))
    set({ user: userData })
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
      if (!parsed?.access_token || !parsed?.refresh_token) {
        throw new Error('Invalid auth token data')
      }

      set({ user: parsed, initializing: false })
    } catch {
      localStorage.removeItem('neuralchat_user')
      set({ user: null, initializing: false })
    }
  },
}))

export default useAuthStore

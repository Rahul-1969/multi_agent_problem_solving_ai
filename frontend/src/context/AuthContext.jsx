/* eslint-disable react-refresh/only-export-components */
import { createContext, useEffect, useContext, useCallback } from 'react'
import useAuthStore from '../store/authStore'
import useChatStore from '../store/chatStore'
import authService from '../services/authService'

export const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export default function AuthProvider({ children }) {
  const { user, initializing, login, logout: storeLogout, verifySession } = useAuthStore()

  const logout = useCallback(async () => {
    await authService.logout()
    storeLogout()
    useChatStore.getState().clearComparison()
  }, [storeLogout])

  useEffect(() => {
    void verifySession()
  }, [verifySession])

  return (
    <AuthContext.Provider value={{ user, login, logout, initializing }}>
      {children}
    </AuthContext.Provider>
  )
}

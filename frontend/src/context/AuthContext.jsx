/* eslint-disable react-refresh/only-export-components */
import { createContext, useEffect, useContext } from 'react'
import useAuthStore from '../store/authStore'

export const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export default function AuthProvider({ children }) {
  const { user, initializing, login, logout, verifySession } = useAuthStore()

  useEffect(() => {
    void verifySession()
  }, [verifySession])

  return (
    <AuthContext.Provider value={{ user, login, logout, initializing }}>
      {children}
    </AuthContext.Provider>
  )
}

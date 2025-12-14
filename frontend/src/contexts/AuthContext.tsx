import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

interface User {
  id: number
  email: string
  full_name: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (email: string, password: string, fullName: string, role: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Optionally fetch user info
    }
  }, [token])

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/token', {
      email,
      password
    })
    const { access_token } = response.data
    setToken(access_token)
    localStorage.setItem('token', access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
  }

  const register = async (email: string, password: string, fullName: string, role: string) => {
    await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role
    })
    // After registration, auto-login
    await login(email, password)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        login,
        logout,
        register
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

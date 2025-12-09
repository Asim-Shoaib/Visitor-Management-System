import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api.setToken(token)
      // Verify token is still valid by fetching user info
      verifyToken()
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async () => {
    try {
      // Fetch user info to get role and username
      if (token) {
        const response = await api.get('/auth/me')
        const { user_id, username, role } = response.data
        setUser({ user_id, username, role, token })
      }
      setLoading(false)
    } catch (error) {
      // Only logout on real auth errors; avoid logout on network/DB issues
      if (error.response?.status === 401) {
        logout()
      } else {
        setLoading(false)
      }
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login', { username, password })
      const { token, user_id, username: userUsername, role } = response.data
      
      localStorage.setItem('token', token)
      setToken(token)
      api.setToken(token)
      setUser({ user_id, username: userUsername, role, token })
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    api.setToken(null)
  }

  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!token,
    loading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}



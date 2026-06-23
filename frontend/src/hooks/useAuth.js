import { useState, useEffect, useCallback } from 'react'
import { login as loginAPI, getCurrentUser } from '../api/endpoints.js'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Restore session from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('eap_token')
    const storedUser = localStorage.getItem('eap_user')

    if (token && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser)
        setUser(parsedUser)
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('eap_token')
        localStorage.removeItem('eap_user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (username, password) => {
    const response = await loginAPI(username, password)
    const { access_token, token_type, user: userData } = response.data

    localStorage.setItem('eap_token', access_token)
    localStorage.setItem('eap_user', JSON.stringify(userData || { username, role: 'viewer' }))

    setUser(userData || { username, role: 'viewer' })
    setIsAuthenticated(true)

    return response.data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('eap_token')
    localStorage.removeItem('eap_user')
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout
  }
}

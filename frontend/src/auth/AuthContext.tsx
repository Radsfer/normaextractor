import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { apiJson, clearToken, getToken, setToken, ApiError } from '../api/client'
import type { LoginResponse } from '../api/types'

interface AuthContextValue {
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getToken())

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiJson<LoginResponse>('/auth/login', 'POST', {
        email,
        password,
      })
      setToken(response.access_token)
      setTokenState(response.access_token)
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        throw new Error('E-mail ou senha inválidos')
      }
      throw error
    }
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setTokenState(null)
  }, [])

  const value = useMemo(
    () => ({ isAuthenticated: token !== null, login, logout }),
    [token, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return context
}

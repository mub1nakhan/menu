import { create } from 'zustand'
import { CurrentUser } from '@/types'

function getRoleFromToken(token?: string | null) {
  if (!token) return null
  try {
    const [, payload] = token.split('.')
    if (!payload) return null
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const decoded = JSON.parse(atob(normalized))
    return decoded.role || decoded.role_code || null
  } catch {
    return null
  }
}

interface AuthState {
  user: CurrentUser | null
  role: string | null
  isAuthenticated: boolean
  setUser: (user: CurrentUser) => void
  setTokens: (access: string, refresh: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  role: typeof window !== 'undefined' ? getRoleFromToken(localStorage.getItem('access_token')) : null,
  isAuthenticated: false,

  setUser: (user) => set({ user, role: user.role_code || user.role || null, isAuthenticated: true }),

  setTokens: (access, refresh) => {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    const role = getRoleFromToken(access)
    set({ role, isAuthenticated: Boolean(access && refresh) })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, role: null, isAuthenticated: false })
  },
}))
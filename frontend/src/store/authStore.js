import { create } from 'zustand'
import api from '../api/client'

const useAuthStore = create((set) => ({
  user: null,
  token: sessionStorage.getItem('access_token'),

  setUser: (user) => set({ user }),

  login: (user, accessToken, refreshToken) => {
    sessionStorage.setItem('access_token', accessToken)
    sessionStorage.setItem('refresh_token', refreshToken)
    set({ user, token: accessToken })
  },

  logout: () => {
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    set({ user: null, token: null })
  },

  fetchMe: async () => {
    try {
      const res = await api.get('/auth/me')
      set({ user: res.data })
    } catch {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
      set({ user: null, token: null })
    }
  }
}))

export default useAuthStore
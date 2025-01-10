import { defineStore } from 'pinia'
import api, { setAuthToken } from '../api/client'

export type User = {
  id: number
  email: string
  full_name?: string | null
  role: string
  phone?: string | null
  location?: string | null
  bio?: string | null
  created_at: string
}

const TOKEN_KEY = 'rf_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: localStorage.getItem(TOKEN_KEY) as string | null,
    loading: false
  }),
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.token,
    role: (state) => state.user?.role ?? null
  },
  actions: {
    setSession(token: string | null) {
      this.token = token
      setAuthToken(token)
      if (token) localStorage.setItem(TOKEN_KEY, token)
      else localStorage.removeItem(TOKEN_KEY)
    },
    async fetchMe() {
      if (!this.token) return null
      try {
        const { data } = await api.get<User>('/auth/me')
        this.user = data
        return data
      } catch (error) {
        this.setSession(null)
        this.user = null
        return null
      }
    },
    async initialize() {
      if (this.token) {
        setAuthToken(this.token)
        if (!this.user) await this.fetchMe()
      }
    },
    async login(email: string, password: string) {
      this.loading = true
      try {
        const { data } = await api.post<{ access_token: string; role: string; full_name?: string | null }>('/auth/login', {
          email,
          password
        })
        this.setSession(data.access_token)
        await this.fetchMe()
      } finally {
        this.loading = false
      }
    },
    async register(payload: { email: string; password: string; full_name?: string; phone?: string; location?: string; role: 'candidate' | 'recruiter' }) {
      this.loading = true
      try {
        await api.post('/auth/register', {
          email: payload.email,
          password: payload.password,
          full_name: payload.full_name,
          phone: payload.phone,
          location: payload.location,
          role: payload.role
        })
        await this.login(payload.email, payload.password)
      } finally {
        this.loading = false
      }
    },
    async registerCandidate(payload: { email: string; password: string; full_name?: string; phone?: string; location?: string }) {
      await this.register({ ...payload, role: 'candidate' })
    },
    async registerRecruiter(payload: { email: string; password: string; full_name?: string }) {
      await this.register({ ...payload, role: 'recruiter' })
    },
    async logout() {
      this.setSession(null)
      this.user = null
    }
  }
})

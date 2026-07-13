import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { login as apiLogin, register as apiRegister, getMe, type UserInfo } from '@/api/auth'

interface AuthState {
  token: string | null
  user: UserInfo | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string, email: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  studentId: () => number | null
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        const result = await apiLogin(username, password)
        set({ token: result.token, isAuthenticated: true })
        await get().fetchUser()
      },

      register: async (username: string, password: string, email: string) => {
        const result = await apiRegister(username, password, email)
        set({ token: result.token, isAuthenticated: true })
        await get().fetchUser()
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
      },

      fetchUser: async () => {
        try {
          const userInfo = await getMe()
          set({ user: userInfo, isAuthenticated: true })
        } catch (error) {
          console.error('Failed to fetch user:', error)
          set({ token: null, user: null, isAuthenticated: false })
        }
      },

      studentId: () => {
        return get().user?.student_id ?? null
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

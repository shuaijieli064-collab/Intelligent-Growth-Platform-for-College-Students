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
        set({ token: result.token, isAuthenticated: true, user: null })
        await get().fetchUser()
      },

      register: async (username: string, password: string, email: string) => {
        const result = await apiRegister(username, password, email)
        set({ token: result.token, isAuthenticated: true, user: null })
        await get().fetchUser()
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
      },

      fetchUser: async () => {
        if (!get().token) return
        try {
          const userInfo = await getMe()
          set({ user: userInfo, isAuthenticated: true })
        } catch {
          // 无论何种错误，都不保留可能不匹配的旧 user
          set({ user: null, isAuthenticated: Boolean(get().token) })
        }
      },

      studentId: () => {
        return get().user?.student_id ?? null
      },
    }),
    {
      name: 'auth-storage',
      // 只持久化 token 与用户信息；isAuthenticated 由 token 派生，
      // 避免本地篡改布尔值绕过前端路由守卫
      partialize: (state) => ({ token: state.token, user: state.user }),
      merge: (persisted, current) => {
        const p = (persisted ?? {}) as { token?: string | null; user?: UserInfo | null }
        return {
          ...current,
          ...p,
          isAuthenticated: Boolean(p.token),
        }
      },
    }
  )
)

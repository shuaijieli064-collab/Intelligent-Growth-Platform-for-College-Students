import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import { router } from '@/router'
import { useTheme } from '@/hooks/useTheme'
import { useAuthStore } from '@/store/authStore'

function App() {
  useTheme()

  // 启动时校验已保存的 token 是否有效（失效则由 401 处理清理）
  useEffect(() => {
    useAuthStore.getState().fetchUser()
  }, [])

  return <RouterProvider router={router} />
}

export default App

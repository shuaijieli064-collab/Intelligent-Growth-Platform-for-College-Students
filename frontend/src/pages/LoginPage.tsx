import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password) {
      setError('请输入用户名和密码')
      return
    }

    setLoading(true)
    setError(null)
    try {
      await login(username.trim(), password)
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err?.message || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 transition-theme relative overflow-hidden bg-bg-surface">
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background:
            'radial-gradient(600px at 12% 8%, rgba(217,119,6,0.14), transparent 60%), radial-gradient(560px at 88% 90%, rgba(184,97,10,0.12), transparent 60%), radial-gradient(400px at 70% 20%, rgba(217,119,6,0.07), transparent 60%)',
        }}
      />
      <div className="w-full max-w-md relative">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-lg"
            style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
          >
            <span className="text-white text-3xl font-bold">智</span>
          </div>
          <h1 className="text-2xl font-bold text-text-primary">欢迎回来</h1>
          <p className="text-text-muted mt-2 text-sm">登录你的智能成长平台账号</p>
        </div>

        <div className="bg-bg-card rounded-2xl shadow-[0_20px_50px_-16px_rgba(16,24,40,0.18)] border border-border-default p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="px-4 py-3 rounded-lg text-sm bg-danger-light text-danger border border-danger/30">
                {error}
              </div>
            )}

            <Input
              label="用户名"
              type="text"
              placeholder="请输入用户名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />

            <Input
              label="密码"
              type="password"
              placeholder="请输入密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={loading}
              disabled={loading}
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            还没有账号？
            <Link
              to="/register"
              className="font-medium ml-1 hover:underline text-accent-text"
            >
              立即注册
            </Link>
          </p>
        </div>

        <p className="text-center text-xs text-text-muted mt-6">
          大学生智能成长平台 · 让成长可见
        </p>
      </div>
    </div>
  )
}

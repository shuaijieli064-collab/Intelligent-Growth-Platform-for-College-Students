import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export default function RegisterPage() {
  const navigate = useNavigate()
  const register = useAuthStore((state) => state.register)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!username.trim()) {
      setError('请输入用户名')
      return
    }
    if (username.trim().length < 3) {
      setError('用户名至少需要 3 个字符')
      return
    }
    if (!password) {
      setError('请输入密码')
      return
    }
    if (password.length < 6) {
      setError('密码至少需要 6 个字符')
      return
    }
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }
    if (!email.trim()) {
      setError('请输入邮箱')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError('请输入有效的邮箱地址')
      return
    }

    setLoading(true)
    try {
      await register(username.trim(), password, email.trim())
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err?.message || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 transition-theme"
      style={{ backgroundColor: '#FAF9F5' }}
    >
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4 shadow-md"
            style={{ background: 'linear-gradient(135deg, #D97757, #B85A3E)' }}
          >
            <span className="text-white text-2xl font-bold">智</span>
          </div>
          <h1 className="text-2xl font-bold text-text-primary">创建账号</h1>
          <p className="text-text-muted mt-2 text-sm">开启你的智能成长之旅</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-border-default p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="px-4 py-3 rounded-lg text-sm"
                style={{
                  backgroundColor: '#FDF2F0',
                  color: '#C53030',
                  border: '1px solid #F4C4BE',
                }}
              >
                {error}
              </div>
            )}

            <Input
              label="用户名"
              type="text"
              placeholder="至少 3 个字符"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />

            <Input
              label="邮箱"
              type="email"
              placeholder="请输入邮箱地址"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />

            <Input
              label="密码"
              type="password"
              placeholder="至少 6 个字符"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required
            />

            <Input
              label="确认密码"
              type="password"
              placeholder="请再次输入密码"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              required
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={loading}
              disabled={loading}
            >
              {loading ? '注册中...' : '注册'}
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            已有账号？
            <Link
              to="/login"
              className="font-medium ml-1 hover:underline"
              style={{ color: '#D97757' }}
            >
              立即登录
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

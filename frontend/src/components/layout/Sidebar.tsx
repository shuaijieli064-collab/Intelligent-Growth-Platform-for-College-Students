import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useTheme } from '@/hooks/useTheme'
import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'

interface NavItem {
  path: string
  label: string
  icon: string
}

const navItems: NavItem[] = [
  { path: '/data-entry', label: '数据录入', icon: '📝' },
  { path: '/dashboard', label: '首页仪表盘', icon: '🏠' },
  { path: '/digital-twin', label: '数字孪生', icon: '👤' },
  { path: '/grade-predict', label: '成绩预测', icon: '📊' },
  { path: '/knowledge-graph', label: '知识图谱', icon: '🧠' },
  { path: '/ai-coach', label: 'AI 学习教练', icon: '🤖' },
  { path: '/risk-warning', label: '风险预警', icon: '⚠' },
  { path: '/study-plan', label: '学习计划', icon: '📋' },
  { path: '/resource', label: '资源推荐', icon: '💡' },
  { path: '/focus-monitor', label: '专注度监测', icon: '🎯' },
  { path: '/growth-archive', label: '成长档案', icon: '📁' },
  { path: '/visualization', label: '数据可视化', icon: '📈' },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { isDark, toggleTheme } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  useEffect(() => {
    setUserMenuOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleProfile = () => {
    navigate('/data-entry?tab=profile')
    onClose()
  }

  const handleSettings = () => {
    navigate('/settings')
    onClose()
  }

  const displayName = user?.name || user?.username || '用户'
  const displayMajor = user?.major || ''
  const displayGrade = user?.grade_level || ''
  const avatarChar = displayName[0] || '?'

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/50 z-30 lg:hidden transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />

      <aside
        className={`fixed left-0 top-0 h-full bg-bg-sidebar border-r border-border-default flex flex-col transition-theme z-40
          w-[260px]
          transform transition-transform duration-300 ease-out
          lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="h-16 flex items-center px-5 border-b border-border-default">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white text-lg font-bold shadow-md">
              智
            </div>
            <div>
              <h1 className="text-lg font-bold text-text-primary tracking-wide">
                智能成长平台
              </h1>
            </div>
          </div>
        </div>

        <div className="px-3 py-3 border-b border-border-default">
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-bg-card border border-border-default hover:border-accent-primary/30 transition-all duration-200"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white font-semibold text-sm">
                {avatarChar}
              </div>
              <div className="flex-1 text-left">
                <div className="text-sm font-medium text-text-primary">
                  {displayName}
                </div>
                <div className="text-xs text-text-muted">
                  {displayGrade || displayMajor ? `${displayGrade} ${displayMajor}`.trim() : user?.email || ''}
                </div>
              </div>
              <svg
                className="w-4 h-4 text-text-muted transition-transform duration-200"
                style={{ transform: userMenuOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {userMenuOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-bg-card border border-border-default rounded-lg shadow-lg overflow-hidden z-30 animate-scale-in">
                <button
                  onClick={handleProfile}
                  className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-bg-hover transition-colors duration-150 text-left"
                >
                  <span className="text-base">👤</span>
                  <span className="text-sm font-medium text-text-primary">个人信息</span>
                </button>
                <div className="border-t border-border-default" />
                <button
                  onClick={handleSettings}
                  className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-bg-hover transition-colors duration-150 text-left"
                >
                  <span className="text-base">⚙️</span>
                  <span className="text-sm font-medium text-text-primary">设置</span>
                </button>
                <div className="border-t border-border-default" />
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-danger/10 transition-colors duration-150 text-left"
                >
                  <span className="text-base">🚪</span>
                  <span className="text-sm font-medium text-danger">退出登录</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-3 px-2">
          <div className="space-y-0.5">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className="flex items-center gap-3 px-3 py-3 text-sm font-medium transition-all duration-200"
                  style={{
                    borderLeftWidth: '3px',
                    borderLeftStyle: 'solid',
                    borderLeftColor: isActive ? 'var(--color-accent-primary)' : 'transparent',
                    borderRadius: '0 8px 8px 0',
                    backgroundColor: isActive ? 'var(--color-accent-light)' : 'transparent',
                    color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)'
                      e.currentTarget.style.color = 'var(--color-text-primary)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent'
                      e.currentTarget.style.color = 'var(--color-text-secondary)'
                    }
                  }}
                >
                  <span className={`w-7 h-7 rounded-md flex items-center justify-center text-sm flex-shrink-0 border transition-colors duration-200 ${
                    isActive
                      ? 'bg-bg-card border-accent-primary/40 shadow-sm'
                      : 'bg-bg-card/70 border-border-default'
                  }`}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </div>
        </nav>

        <div className="p-3 border-t border-border-default">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-text-muted hover:bg-bg-hover hover:text-text-secondary transition-all duration-200"
          >
            <span>{isDark ? '☀️' : '🌙'}</span>
            <span>{isDark ? '浅色模式' : '深色模式'}</span>
            <span className="ml-auto opacity-70">让成长可见</span>
          </button>
        </div>
      </aside>
    </>
  )
}

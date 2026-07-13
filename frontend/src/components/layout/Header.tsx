import { useTheme } from '@/hooks/useTheme'

interface HeaderProps {
  title?: string
  onMenuClick?: () => void
}

export function Header({ title, onMenuClick }: HeaderProps) {
  const { isDark, toggleTheme } = useTheme()

  return (
    <header className="h-16 bg-bg-surface/80 backdrop-blur-md border-b border-border-default flex items-center justify-between px-4 md:px-6 sticky top-0 z-10 transition-theme">
      <div className="flex items-center gap-3 md:gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-bg-hover text-text-secondary hover:text-text-primary transition-all duration-200"
          title="菜单"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        {title && (
          <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
        )}
      </div>
      <div className="flex items-center gap-2 md:gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-bg-hover text-text-secondary hover:text-text-primary transition-all duration-200"
          title={isDark ? '切换到浅色模式' : '切换到深色模式'}
        >
          <span className="text-xl">{isDark ? '☀️' : '🌙'}</span>
        </button>
        <div className="w-px h-6 bg-border-default hidden sm:block" />
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-accent-text font-semibold text-sm">
            管
          </div>
          <span className="text-sm text-text-secondary hidden md:inline">管理员</span>
        </div>
      </div>
    </header>
  )
}

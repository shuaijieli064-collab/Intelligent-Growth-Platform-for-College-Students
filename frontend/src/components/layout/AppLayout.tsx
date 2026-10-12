import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { useState, useEffect } from 'react'

const pageTitles: Record<string, string> = {
  '/data-entry': '数据录入',
  '/dashboard': '首页仪表盘',
  '/digital-twin': '数字孪生',
  '/grade-predict': '成绩预测',
  '/knowledge-graph': '知识图谱',
  '/ai-coach': 'AI 学习教练',
  '/risk-warning': '风险预警',
  '/study-plan': '学习计划',
  '/resource': '资源推荐',
  '/focus-monitor': '专注度监测',
  '/growth-archive': '成长档案',
  '/visualization': '数据可视化',
  '/settings': '设置',
}

export function AppLayout() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || '智能成长平台'
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [key, setKey] = useState(0)

  useEffect(() => {
    setKey(prev => prev + 1)
    window.scrollTo(0, 0)
  }, [location.pathname])

  const closeSidebar = () => setSidebarOpen(false)
  const toggleSidebar = () => setSidebarOpen(prev => !prev)

  return (
    <div className="min-h-screen bg-bg-surface transition-theme">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="lg:ml-[260px] flex flex-col min-h-screen">
        <Header title={title} onMenuClick={toggleSidebar} />
        <main 
          key={key}
          className="flex-1 p-4 sm:p-6 md:p-8 animate-fade-in"
        >
          <div className="max-w-[1600px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

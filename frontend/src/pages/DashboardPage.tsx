import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { useAuthStore } from '@/store/authStore'
import { getDashboard } from '@/api/dashboard'
import type { DashboardData, RiskAlertItem } from '@/types'

const riskLevelMap: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' | 'accent' }> = {
  LOW: { label: '低风险', variant: 'success' },
  MEDIUM: { label: '中风险', variant: 'warning' },
  HIGH: { label: '高风险', variant: 'danger' },
  CRITICAL: { label: '严重风险', variant: 'danger' },
}

const alertTypeMap: Record<string, string> = {
  学业: '学业预警',
  健康: '体质预警',
  心理: '心理预警',
  社交: '社交预警',
}

function getHealthColor(score: number): string {
  if (score >= 80) return 'text-success'
  if (score >= 60) return 'text-warning'
  return 'text-danger'
}

function getHealthVariant(score: number): 'success' | 'warning' | 'danger' {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function DimensionCard({
  title,
  icon,
  score,
  description,
  tint,
}: {
  title: string
  icon: string
  score: number
  description: string
  tint: 'accent' | 'info' | 'success' | 'warning'
}) {
  const tintClasses = {
    accent: 'bg-accent-light',
    info: 'bg-info-light',
    success: 'bg-success-light',
    warning: 'bg-warning-light',
  }

  return (
    <Card hoverable>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-xl ${tintClasses[tint]} flex items-center justify-center text-2xl flex-shrink-0`}>
            {icon}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
              <span className={`text-lg font-bold ${getHealthColor(score)}`}>
                {score.toFixed(1)}
              </span>
            </div>
            <p className="text-xs text-text-muted mt-1">{description}</p>
            <div className="mt-3">
              <Progress value={score} variant={getHealthVariant(score)} size="sm" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function AlertItem({ alert }: { alert: RiskAlertItem }) {
  const riskInfo = riskLevelMap[alert.risk_level] || { label: alert.risk_level, variant: 'default' as const }
  const alertTypeLabel = alertTypeMap[alert.alert_type] || alert.alert_type

  return (
    <div className="flex items-start gap-3 p-4 rounded-lg bg-bg-hover/30 hover:bg-bg-hover/50 transition-colors duration-200">
      <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
        alert.is_resolved ? 'bg-success' : riskInfo.variant === 'danger' ? 'bg-danger' : riskInfo.variant === 'warning' ? 'bg-warning' : 'bg-info'
      }`} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-text-primary">{alertTypeLabel}</span>
          <Badge variant={alert.is_resolved ? 'success' : riskInfo.variant} size="sm">
            {alert.is_resolved ? '已处理' : riskInfo.label}
          </Badge>
        </div>
        <p className="text-sm text-text-secondary mt-1 line-clamp-2">{alert.alert_message}</p>
        <p className="text-xs text-text-muted mt-1.5">{formatDate(alert.created_at)}</p>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-bg-card border border-border-default rounded-xl p-6 animate-pulse">
      <div className="h-4 bg-bg-active rounded w-24 mb-4" />
      <div className="h-10 bg-bg-active rounded w-20 mb-2" />
      <div className="h-3 bg-bg-active rounded w-32" />
    </div>
  )
}

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await getDashboard()
        setData(result)
      } catch (err) {
        setError('加载数据失败，请稍后重试')
        console.error('Failed to fetch dashboard:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const riskInfo = data ? riskLevelMap[data.risk_level] || { label: data.risk_level, variant: 'default' as const } : null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">
            欢迎回来，{user?.name || user?.username || '同学'}！
          </h1>
          <p className="text-text-muted mt-1">
            查看你的成长健康状况和最新动态
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-danger-light text-danger border border-danger/30">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : data ? (
          <>
            <Card hoverable>
              <CardContent className="pt-6">
                <p className="text-sm text-text-muted font-medium uppercase tracking-wide">综合健康度</p>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className={`text-4xl font-bold ${getHealthColor(data.overall_health)}`}>
                    {data.overall_health.toFixed(1)}
                  </span>
                  <span className="text-lg text-text-muted">/100</span>
                </div>
                <div className="mt-3">
                  <Progress value={data.overall_health} variant={getHealthVariant(data.overall_health)} />
                </div>
                <p className="text-sm text-text-muted mt-3">总体成长健康状态</p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <p className="text-sm text-text-muted font-medium uppercase tracking-wide">风险等级</p>
                <div className="mt-3">
                  <Badge variant={riskInfo?.variant || 'default'} size="md" className="text-base px-3 py-1.5">
                    {riskInfo?.label || '未知'}
                  </Badge>
                </div>
                <p className="text-sm text-text-muted mt-4">
                  {data.risk_level === 'LOW' && '状态良好，继续保持！'}
                  {data.risk_level === 'MEDIUM' && '需要关注，建议查看详情'}
                  {data.risk_level === 'HIGH' && '风险较高，请及时干预'}
                  {data.risk_level === 'CRITICAL' && '风险严重，请立即处理'}
                </p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <p className="text-sm text-text-muted font-medium uppercase tracking-wide">活跃告警</p>
                <p className={`text-4xl font-bold mt-2 ${data.active_alert_count > 0 ? 'text-danger' : 'text-success'}`}>
                  {data.active_alert_count}
                </p>
                <p className="text-sm text-text-muted mt-3">
                  {data.active_alert_count > 0 ? '条待处理告警' : '暂无待处理告警'}
                </p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <p className="text-sm text-text-muted font-medium uppercase tracking-wide">学业健康</p>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className={`text-4xl font-bold ${getHealthColor(data.dimensions.academic)}`}>
                    {data.dimensions.academic.toFixed(1)}
                  </span>
                  <span className="text-lg text-text-muted">/100</span>
                </div>
                <div className="mt-3">
                  <Progress value={data.dimensions.academic} variant={getHealthVariant(data.dimensions.academic)} />
                </div>
                <p className="text-sm text-text-muted mt-3">学业维度健康评分</p>
              </CardContent>
            </Card>
          </>
        ) : (
          <div className="col-span-full text-center py-8 text-text-muted">
            请先选择学生
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>四维度健康详情</CardTitle>
          <CardDescription>学业、身体、心理、社交四个维度的健康评估</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : data ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <DimensionCard
                title="学业健康"
                icon="📚"
                score={data.dimensions.academic}
                description="基于学习成绩、学习进度等综合评估"
                tint="info"
              />
              <DimensionCard
                title="身体健康"
                icon="💪"
                score={data.dimensions.physical}
                description="基于运动、睡眠、作息等综合评估"
                tint="success"
              />
              <DimensionCard
                title="心理健康"
                icon="💛"
                score={data.dimensions.mental}
                description="基于情绪、压力、专注度等综合评估"
                tint="warning"
              />
              <DimensionCard
                title="社交健康"
                icon="👥"
                score={data.dimensions.social}
                description="基于社交活动、人际关系等综合评估"
                tint="accent"
              />
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted">
              暂无数据
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>最近风险告警</CardTitle>
              <CardDescription>最近 10 条风险预警记录</CardDescription>
            </div>
            <Badge variant="info" size="sm">
              共 {data?.recent_alerts.length || 0} 条
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 rounded-lg bg-bg-hover/30 animate-pulse">
                  <div className="h-4 bg-bg-active rounded w-32 mb-2" />
                  <div className="h-3 bg-bg-active rounded w-full mb-1" />
                  <div className="h-3 bg-bg-active rounded w-3/4" />
                </div>
              ))}
            </div>
          ) : data && data.recent_alerts.length > 0 ? (
            <div className="space-y-2">
              {data.recent_alerts.map((alert) => (
                <AlertItem key={alert.alert_id} alert={alert} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted">
              暂无告警记录
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

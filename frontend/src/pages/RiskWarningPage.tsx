import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import {
  getAlerts,
  resolveAlert,
  deleteAlert,
  batchDeleteAlerts,
  type RiskAlert,
  type AlertFilter,
} from '@/api/riskWarning'

const riskLevelMap: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  LOW: { label: '低风险', variant: 'success' },
  MEDIUM: { label: '中风险', variant: 'warning' },
  HIGH: { label: '高风险', variant: 'danger' },
  CRITICAL: { label: '严重风险', variant: 'danger' },
}

const alertTypeMap: Record<string, string> = {
  学业: '学业预警',
  健康: '健康预警',
  心理: '心理预警',
  社交: '社交预警',
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

function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  return (
    <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg animate-fade-in ${
      type === 'success' ? 'bg-success text-white' : 'bg-danger text-white'
    }`}>
      {message}
      <button type="button" className="ml-3 opacity-80 hover:opacity-100" onClick={onClose}>×</button>
    </div>
  )
}

export default function RiskWarningPage() {
  const [alerts, setAlerts] = useState<RiskAlert[]>([])
  const [filter, setFilter] = useState<AlertFilter>('all')
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      const result = await getAlerts(filter)
      setAlerts(result)
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [filter])

  const handleResolve = async (alertId: number) => {
    setActionLoading(true)
    try {
      await resolveAlert(alertId)
      setAlerts(prev => prev.map(a =>
        a.alert_id === alertId ? { ...a, is_resolved: true } : a
      ))
      setSelectedIds(prev => prev.filter(id => id !== alertId))
      setToast({ message: '告警已标记为已处理', type: 'success' })
    } catch (error) {
      console.error('Failed to resolve alert:', error)
      const detail = (error as { message?: string })?.message
      setToast({ message: detail || '处理失败，请稍后重试', type: 'error' })
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (alertId: number) => {
    if (!confirm('确定要删除这条告警吗？')) return

    setActionLoading(true)
    try {
      await deleteAlert(alertId)
      setAlerts(prev => prev.filter(a => a.alert_id !== alertId))
      setSelectedIds(prev => prev.filter(id => id !== alertId))
      setToast({ message: '告警已删除', type: 'success' })
    } catch (error) {
      console.error('Failed to delete alert:', error)
      const detail = (error as { message?: string })?.message
      setToast({ message: detail || '删除失败，请稍后重试', type: 'error' })
    } finally {
      setActionLoading(false)
    }
  }

  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) return
    if (!confirm(`确定要删除选中的 ${selectedIds.length} 条告警吗？`)) return

    setActionLoading(true)
    try {
      await batchDeleteAlerts(selectedIds)
      setAlerts(prev => prev.filter(a => !selectedIds.includes(a.alert_id!)))
      setSelectedIds([])
      setToast({ message: '批量删除成功', type: 'success' })
    } catch (error) {
      console.error('Failed to batch delete:', error)
      const detail = (error as { message?: string })?.message
      setToast({ message: detail || '批量删除失败，请稍后重试', type: 'error' })
    } finally {
      setActionLoading(false)
    }
  }

  const toggleSelect = (alertId: number) => {
    setSelectedIds(prev =>
      prev.includes(alertId)
        ? prev.filter(id => id !== alertId)
        : [...prev, alertId]
    )
  }

  const toggleSelectAll = () => {
    const unresolvedAlerts = alerts.filter(a => !a.is_resolved).map(a => a.alert_id!)
    if (selectedIds.length === unresolvedAlerts.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(unresolvedAlerts)
    }
  }

  const unresolvedCount = alerts.filter(a => !a.is_resolved).length
  const unresolvedAlerts = alerts.filter(a => !a.is_resolved)

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">⚠️</span>
          风险预警
        </h1>
        <p className="text-text-muted mt-1">实时监控学习状态，及时发现风险</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card hoverable>
          <CardContent className="pt-6">
            <p className="text-sm text-text-muted font-medium uppercase tracking-wide">全部告警</p>
            <p className="text-3xl font-bold text-text-primary mt-2">{alerts.length}</p>
            <p className="text-sm text-text-muted mt-2">历史告警总数</p>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="pt-6">
            <p className="text-sm text-text-muted font-medium uppercase tracking-wide">待处理</p>
            <p className={`text-3xl font-bold mt-2 ${unresolvedCount > 0 ? 'text-danger' : 'text-success'}`}>
              {unresolvedCount}
            </p>
            <p className="text-sm text-text-muted mt-2">
              {unresolvedCount > 0 ? '需要及时处理' : '全部已处理'}
            </p>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="pt-6">
            <p className="text-sm text-text-muted font-medium uppercase tracking-wide">高风险</p>
            <p className="text-3xl font-bold text-danger mt-2">
              {alerts.filter(a => (a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL') && !a.is_resolved).length}
            </p>
            <p className="text-sm text-text-muted mt-2">需要优先处理</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>告警列表</CardTitle>
              <CardDescription>所有风险预警记录</CardDescription>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex gap-1 p-1 bg-bg-hover rounded-lg">
                {(['all', 'unresolved', 'resolved'] as AlertFilter[]).map(f => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`px-3 py-1.5 text-sm rounded-md transition-all ${
                      filter === f
                        ? 'bg-bg-card text-text-primary font-medium shadow-sm'
                        : 'text-text-muted hover:text-text-secondary'
                    }`}
                  >
                    {f === 'all' ? '全部' : f === 'unresolved' ? '未处理' : '已处理'}
                  </button>
                ))}
              </div>
              {selectedIds.length > 0 && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleBatchDelete}
                  isLoading={actionLoading}
                >
                  批量删除 ({selectedIds.length})
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="p-4 rounded-lg bg-bg-hover/30 animate-pulse">
                  <div className="h-4 bg-bg-active rounded w-32 mb-2" />
                  <div className="h-3 bg-bg-active rounded w-full mb-1" />
                  <div className="h-3 bg-bg-active rounded w-3/4" />
                </div>
              ))}
            </div>
          ) : alerts.length > 0 ? (
            <div className="space-y-3">
              {filter !== 'resolved' && unresolvedAlerts.length > 0 && (
                <div className="flex items-center gap-3 px-2">
                  <input
                    type="checkbox"
                    checked={selectedIds.length === unresolvedAlerts.length && unresolvedAlerts.length > 0}
                    onChange={toggleSelectAll}
                    className="w-4 h-4 rounded border-border-default text-accent-primary focus:ring-accent-primary/20"
                  />
                  <span className="text-sm text-text-muted">全选未处理</span>
                </div>
              )}
              {alerts.map(alert => {
                const riskInfo = riskLevelMap[alert.risk_level] || { label: alert.risk_level, variant: 'warning' as const }
                const alertTypeLabel = alertTypeMap[alert.alert_type] || alert.alert_type

                return (
                  <div
                    key={alert.alert_id}
                    className={`flex items-start gap-4 p-4 rounded-lg transition-colors ${
                      alert.is_resolved ? 'bg-bg-hover/20 opacity-70' : 'bg-bg-hover/30 hover:bg-bg-hover/50'
                    }`}
                  >
                    {!alert.is_resolved && (
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(alert.alert_id!)}
                        onChange={() => toggleSelect(alert.alert_id!)}
                        className="mt-1 w-4 h-4 rounded border-border-default text-accent-primary focus:ring-accent-primary/20"
                      />
                    )}
                    {alert.is_resolved && <div className="w-4" />}

                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      alert.is_resolved ? 'bg-success' :
                      riskInfo.variant === 'danger' ? 'bg-danger animate-pulse' :
                      riskInfo.variant === 'warning' ? 'bg-warning' : 'bg-info'
                    }`} />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-text-primary">{alertTypeLabel}</span>
                        <Badge variant={alert.is_resolved ? 'success' : riskInfo.variant} size="sm">
                          {alert.is_resolved ? '已处理' : riskInfo.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-text-secondary mt-1">{alert.alert_message}</p>
                      <p className="text-xs text-text-muted mt-2">{formatDate(alert.created_at)}</p>
                    </div>

                    <div className="flex gap-2 flex-shrink-0">
                      {!alert.is_resolved && (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => handleResolve(alert.alert_id!)}
                          disabled={actionLoading}
                        >
                          标记已处理
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(alert.alert_id!)}
                        disabled={actionLoading}
                        className="text-danger hover:text-danger hover:bg-danger/10"
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-text-muted">
              <span className="text-5xl mb-4 block">✅</span>
              <p className="font-medium text-text-secondary">暂无告警记录</p>
              <p className="text-sm mt-1">继续保持良好的学习状态！</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

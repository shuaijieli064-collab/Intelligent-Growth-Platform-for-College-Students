import { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Progress } from '@/components/ui/Progress'
import { useTheme } from '@/hooks/useTheme'
import { getDigitalTwin, getDigitalTwinHistory, type DigitalTwinData, type HealthAssessmentItem } from '@/api/digitalTwin'

const riskLevelMap: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  LOW: { label: '低风险', variant: 'success' },
  MEDIUM: { label: '中风险', variant: 'warning' },
  HIGH: { label: '高风险', variant: 'danger' },
  CRITICAL: { label: '严重风险', variant: 'danger' },
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
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export default function DigitalTwinPage() {
  const { isDark } = useTheme()
  const [data, setData] = useState<DigitalTwinData | null>(null)
  const [history, setHistory] = useState<HealthAssessmentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(false)

  const axisTextColor = isDark ? '#b4b4b4' : '#555555'
  const axisMutedColor = isDark ? '#9a9aa3' : '#888888'
  const axisLineColor = isDark ? '#3a3c41' : '#e8e5e1'

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await getDigitalTwin()
        setData(result)
      } catch (error) {
        console.error('Failed to fetch digital twin:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  useEffect(() => {
    const fetchHistory = async () => {
      setHistoryLoading(true)
      try {
        const result = await getDigitalTwinHistory(1, 30)
        setHistory(result.items)
      } catch (error) {
        console.error('Failed to fetch history:', error)
      } finally {
        setHistoryLoading(false)
      }
    }

    fetchHistory()
  }, [])

  const radarOption = data ? {
    radar: {
      indicator: [
        { name: '学业健康', max: 100 },
        { name: '身体健康', max: 100 },
        { name: '心理健康', max: 100 },
        { name: '社交健康', max: 100 },
      ],
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: axisTextColor,
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: axisLineColor,
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['transparent'],
        },
      },
      axisLine: {
        lineStyle: {
          color: axisLineColor,
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              data.dimensions.academic,
              data.dimensions.physical,
              data.dimensions.mental,
              data.dimensions.social,
            ],
            name: '健康度',
            areaStyle: {
              color: 'rgba(217, 119, 6, 0.2)',
            },
            lineStyle: {
              color: '#d97706',
              width: 2,
            },
            itemStyle: {
              color: '#d97706',
            },
          },
        ],
      },
    ],
    tooltip: {
      trigger: 'item',
    },
  } : {}

  const trendOption = history.length > 0 ? {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['综合健康', '学业', '身体', '心理', '社交'],
      textStyle: {
        color: axisTextColor,
      },
      top: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...history].reverse().map(h => formatDate(h.assessment_date)),
      axisLabel: {
        color: axisMutedColor,
        fontSize: 10,
      },
      axisLine: {
        lineStyle: {
          color: axisLineColor,
        },
      },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        color: axisMutedColor,
      },
      splitLine: {
        lineStyle: {
          color: axisLineColor,
        },
      },
    },
    series: [
      {
        name: '综合健康',
        type: 'line',
        smooth: true,
        data: [...history].reverse().map(h => h.overall_health),
        lineStyle: { width: 2, color: '#d97706' },
        itemStyle: { color: '#d97706' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(217, 119, 6, 0.3)' },
              { offset: 1, color: 'rgba(217, 119, 6, 0.05)' },
            ],
          },
        },
      },
      {
        name: '学业',
        type: 'line',
        smooth: true,
        data: [...history].reverse().map(h => h.academic_score),
        lineStyle: { width: 1.5, color: '#10b981' },
        itemStyle: { color: '#10b981' },
      },
      {
        name: '身体',
        type: 'line',
        smooth: true,
        data: [...history].reverse().map(h => h.physical_score),
        lineStyle: { width: 1.5, color: '#f59e0b' },
        itemStyle: { color: '#f59e0b' },
      },
      {
        name: '心理',
        type: 'line',
        smooth: true,
        data: [...history].reverse().map(h => h.mental_score),
        lineStyle: { width: 1.5, color: '#ec4899' },
        itemStyle: { color: '#ec4899' },
      },
      {
        name: '社交',
        type: 'line',
        smooth: true,
        data: [...history].reverse().map(h => h.social_score),
        lineStyle: { width: 1.5, color: '#8b5cf6' },
        itemStyle: { color: '#8b5cf6' },
      },
    ],
  } : {}

  const riskInfo = data ? riskLevelMap[data.risk_level] || { label: data.risk_level, variant: 'warning' as const } : null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">🧬</span>
          数字孪生
        </h1>
        <p className="text-text-muted mt-1">四维度健康度评估与历史趋势分析</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-bg-card border border-border-default rounded-xl p-6 animate-pulse">
              <div className="h-4 bg-bg-active rounded w-24 mb-4" />
              <div className="h-10 bg-bg-active rounded w-20 mb-2" />
              <div className="h-3 bg-bg-active rounded w-32" />
            </div>
          ))}
        </div>
      ) : data ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-5">
            <Card hoverable className="lg:col-span-1">
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
                <p className="text-sm text-text-muted mt-3">{riskInfo?.label || '未知'}</p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary">学业健康</h4>
                  <span className={`text-lg font-bold ${getHealthColor(data.dimensions.academic)}`}>
                    {data.dimensions.academic.toFixed(1)}
                  </span>
                </div>
                <div className="mt-3">
                  <Progress value={data.dimensions.academic} variant={getHealthVariant(data.dimensions.academic)} size="sm" />
                </div>
                <p className="text-xs text-text-muted mt-2">基于学习成绩综合评估</p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary">身体健康</h4>
                  <span className={`text-lg font-bold ${getHealthColor(data.dimensions.physical)}`}>
                    {data.dimensions.physical.toFixed(1)}
                  </span>
                </div>
                <div className="mt-3">
                  <Progress value={data.dimensions.physical} variant={getHealthVariant(data.dimensions.physical)} size="sm" />
                </div>
                <p className="text-xs text-text-muted mt-2">基于运动、睡眠综合评估</p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary">心理健康</h4>
                  <span className={`text-lg font-bold ${getHealthColor(data.dimensions.mental)}`}>
                    {data.dimensions.mental.toFixed(1)}
                  </span>
                </div>
                <div className="mt-3">
                  <Progress value={data.dimensions.mental} variant={getHealthVariant(data.dimensions.mental)} size="sm" />
                </div>
                <p className="text-xs text-text-muted mt-2">基于情绪、压力综合评估</p>
              </CardContent>
            </Card>

            <Card hoverable>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary">社交健康</h4>
                  <span className={`text-lg font-bold ${getHealthColor(data.dimensions.social)}`}>
                    {data.dimensions.social.toFixed(1)}
                  </span>
                </div>
                <div className="mt-3">
                  <Progress value={data.dimensions.social} variant={getHealthVariant(data.dimensions.social)} size="sm" />
                </div>
                <p className="text-xs text-text-muted mt-2">基于社交活动综合评估</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>四维度雷达图</CardTitle>
                <CardDescription>各维度健康度分布对比</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ReactECharts option={radarOption} style={{ height: '100%', width: '100%' }} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>健康趋势</CardTitle>
                <CardDescription>最近 30 天健康度变化</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  {historyLoading ? (
                    <div className="h-full flex items-center justify-center text-text-muted">
                      加载中...
                    </div>
                  ) : history.length > 0 ? (
                    <ReactECharts option={trendOption} style={{ height: '100%', width: '100%' }} />
                  ) : (
                    <div className="h-full flex items-center justify-center text-text-muted">
                      暂无历史数据
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>历史评估记录</CardTitle>
              <CardDescription>最近的健康评估记录列表</CardDescription>
            </CardHeader>
            <CardContent>
              {historyLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="p-4 rounded-lg bg-bg-hover/30 animate-pulse">
                      <div className="h-4 bg-bg-active rounded w-32 mb-2" />
                      <div className="h-3 bg-bg-active rounded w-full" />
                    </div>
                  ))}
                </div>
              ) : history.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-default">
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">日期</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">综合健康</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">学业</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">身体</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">心理</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">社交</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">风险等级</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map(item => (
                        <tr key={item.assessment_id} className="border-b border-border-default/50 hover:bg-bg-hover/30 transition-colors">
                          <td className="py-3 px-4 text-sm text-text-primary">{formatDate(item.assessment_date)}</td>
                          <td className={`py-3 px-4 text-sm font-medium ${getHealthColor(item.overall_health)}`}>
                            {item.overall_health.toFixed(1)}
                          </td>
                          <td className="py-3 px-4 text-sm text-text-secondary">{item.academic_score.toFixed(1)}</td>
                          <td className="py-3 px-4 text-sm text-text-secondary">{item.physical_score.toFixed(1)}</td>
                          <td className="py-3 px-4 text-sm text-text-secondary">{item.mental_score.toFixed(1)}</td>
                          <td className="py-3 px-4 text-sm text-text-secondary">{item.social_score.toFixed(1)}</td>
                          <td className="py-3 px-4 text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              item.risk_level === 'LOW' ? 'bg-success/10 text-success' :
                              item.risk_level === 'MEDIUM' ? 'bg-warning/10 text-warning' :
                              'bg-danger/10 text-danger'
                            }`}>
                              {riskLevelMap[item.risk_level]?.label || item.risk_level}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-text-muted">
                  暂无历史评估记录
                </div>
              )}
            </CardContent>
          </Card>
        </>
      ) : (
        <div className="text-center py-16 text-text-muted">
          暂无数据
        </div>
      )}
    </div>
  )
}

import { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import ReactECharts from 'echarts-for-react'
import { useTheme } from '@/hooks/useTheme'
import { cssVarRgb } from '@/utils/cssVar'
import { escapeHtml } from '@/utils/safe'
import { getFocusData, type FocusMonitorData } from '@/api/focusMonitor'

const levelColorMap: Record<string, string> = {
  '高度专注 🟢': 'text-success',
  '正常 🟡': 'text-accent-primary',
  '注意力分散 🟠': 'text-warning',
  '严重分心 🔴': 'text-danger',
}

const levelBgMap: Record<string, string> = {
  '高度专注 🟢': 'from-success/20 to-success/5',
  '正常 🟡': 'from-accent-primary/20 to-accent-primary/5',
  '注意力分散 🟠': 'from-warning/20 to-warning/5',
  '严重分心 🔴': 'from-danger/20 to-danger/5',
}

export default function FocusMonitorPage() {
  const { isDark } = useTheme()
  const [data, setData] = useState<FocusMonitorData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await getFocusData()
        setData(result)
      } catch (err) {
        console.error('Failed to fetch focus data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const lineChartOption = useMemo(() => {
    if (!data) return {}

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: cssVarRgb('--bg-card-rgb', 0.95),
        borderColor: cssVarRgb('--border-default-rgb', 0.6),
        textStyle: { color: cssVarRgb('--text-primary-rgb') },
      },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.last_14_days.map(d => d.date.slice(5)),
        axisLine: { lineStyle: { color: cssVarRgb('--border-default-rgb', 0.55) } },
        axisLabel: { color: cssVarRgb('--text-secondary-rgb') },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: cssVarRgb('--border-default-rgb', 0.55) } },
        axisLabel: { color: cssVarRgb('--text-secondary-rgb') },
        splitLine: { lineStyle: { color: cssVarRgb('--border-default-rgb', 0.3) } },
      },
      series: [
        {
          name: '专注指数',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          data: data.last_14_days.map(d => d.focus_score),
          lineStyle: { color: cssVarRgb('--accent-primary-rgb'), width: 3 },
          itemStyle: { color: cssVarRgb('--accent-primary-rgb') },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: cssVarRgb('--accent-primary-rgb', 0.35) },
                { offset: 1, color: cssVarRgb('--accent-primary-rgb', 0.05) },
              ],
            },
          },
        },
      ],
    }
  }, [data, isDark])

  const calendarOption = useMemo(() => {
    if (!data) return {}

    const heatmapData = data.last_30_days.map(d => [d.date, d.focus_score])
    const dates = data.last_30_days.map(d => d.date)

    return {
      tooltip: {
        position: 'top',
        backgroundColor: cssVarRgb('--bg-card-rgb', 0.95),
        borderColor: cssVarRgb('--border-default-rgb', 0.6),
        textStyle: { color: cssVarRgb('--text-primary-rgb') },
        formatter: (params: any) => {
          const date = params.data[0]
          const value = params.data[1]
          return `${escapeHtml(date)}<br/>专注指数: ${Number(value).toFixed(0)}`
        },
      },
      visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: [
            cssVarRgb('--danger-rgb', 0.35),
            cssVarRgb('--warning-rgb', 0.65),
            cssVarRgb('--accent-primary-rgb', 0.85),
            cssVarRgb('--success-rgb'),
          ],
        },
        textStyle: { color: cssVarRgb('--text-secondary-rgb') },
      },
      calendar: {
        top: 30,
        left: 30,
        right: 30,
        cellSize: ['auto', 28],
        range: dates.length > 0 ? [dates[0], dates[dates.length - 1]] : [],
        itemStyle: {
          borderWidth: 2,
          borderColor: cssVarRgb('--bg-base-rgb'),
          borderRadius: 4,
        },
        splitLine: { show: false },
        dayLabel: { color: cssVarRgb('--text-secondary-rgb'), nameMap: 'ZH' },
        monthLabel: { color: cssVarRgb('--text-secondary-rgb') },
        yearLabel: { show: false },
      },
      series: [
        {
          type: 'heatmap',
          coordinateSystem: 'calendar',
          data: heatmapData,
        },
      ],
    }
  }, [data, isDark])

  const trendInfo = useMemo(() => {
    if (!data) return { text: '稳定', color: 'text-text-muted', icon: '➡️' }

    if (data.trend === '上升' || data.trend === '改善中') {
      return { text: '改善中', color: 'text-success', icon: '📈' }
    } else if (data.trend === '下降' || data.trend === '下降中') {
      return { text: '下降中', color: 'text-danger', icon: '📉' }
    }
    return { text: '稳定', color: 'text-accent-primary', icon: '➡️' }
  }, [data])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-bg-active rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card className="h-64">
              <CardContent className="animate-pulse" />
            </Card>
          </div>
          <div className="lg:col-span-2">
            <Card className="h-64">
              <CardContent className="animate-pulse" />
            </Card>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">🎯</span>
          专注度监测
        </h1>
        <p className="text-text-muted mt-1">实时追踪你的学习专注状态</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className={`bg-gradient-to-br ${levelBgMap[data?.level || '正常 🟡']}`}>
          <CardContent className="pt-6">
            <p className="text-text-muted text-sm mb-2">当前专注指数</p>
            <div className="flex items-baseline gap-2">
              <span className="text-6xl font-bold text-text-primary">
                {data?.realtime_score.toFixed(0)}
              </span>
              <span className="text-text-muted text-lg">/ 100</span>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className={`text-lg font-semibold ${levelColorMap[data?.level || '正常 🟡']}`}>
                {data?.level || '正常 🟡'}
              </span>
              <span className={`flex items-center gap-1 text-sm ${trendInfo.color}`}>
                <span>{trendInfo.icon}</span>
                {trendInfo.text}
              </span>
            </div>
          </CardContent>
        </Card>

        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>近 14 天专注趋势</CardTitle>
              <CardDescription>每日专注指数变化</CardDescription>
            </CardHeader>
            <CardContent>
              <ReactECharts
                option={lineChartOption}
                style={{ height: 220 }}
                theme="light"
                notMerge={true}
                lazyUpdate={true}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>30 天专注热力图</CardTitle>
          <CardDescription>颜色越深表示专注度越高</CardDescription>
        </CardHeader>
        <CardContent>
          <ReactECharts
            option={calendarOption}
            style={{ height: 280 }}
            theme="light"
            notMerge={true}
            lazyUpdate={true}
          />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-text-muted text-sm">平均专注指数</p>
            <p className="text-3xl font-bold text-text-primary mt-2">
              {data && data.last_14_days.length > 0 ? (data.last_14_days.reduce((s, d) => s + d.focus_score, 0) / data.last_14_days.length).toFixed(1) : '0'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-text-muted text-sm">最高专注日</p>
            <p className="text-3xl font-bold text-success mt-2">
              {data && data.last_14_days.length > 0 ? Math.max(...data.last_14_days.map(d => d.focus_score)).toFixed(0) : '0'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-text-muted text-sm">稳定天数</p>
            <p className="text-3xl font-bold text-accent-primary mt-2">
              {data ? data.last_14_days.filter(d => d.focus_score >= 70).length : 0}
              <span className="text-lg text-text-muted ml-1">天</span>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

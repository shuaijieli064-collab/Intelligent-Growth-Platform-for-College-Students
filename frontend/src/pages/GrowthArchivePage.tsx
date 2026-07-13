import { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import ReactECharts from 'echarts-for-react'
import {
  getReports,
  generateReport,
  getReportDetail,
  type GrowthReportListItem,
  type GrowthReportDetail,
} from '@/api/growthArchive'

const reportTypeMap: Record<string, { label: string; icon: string }> = {
  weekly: { label: '周报', icon: '📅' },
  monthly: { label: '月报', icon: '📆' },
  semester: { label: '学期报告', icon: '📚' },
}

export default function GrowthArchivePage() {
  const [reports, setReports] = useState<GrowthReportListItem[]>([])
  const [selectedReport, setSelectedReport] = useState<GrowthReportDetail | null>(null)
  const [reportType, setReportType] = useState('weekly')
  const [generating, setGenerating] = useState(false)
  const [loadingReports, setLoadingReports] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    const fetchReports = async () => {
      setLoadingReports(true)
      try {
        const result = await getReports()
        setReports(result)
        if (result.length > 0) {
          await loadReport(result[0].id)
        }
      } catch (err) {
        console.error('Failed to fetch reports:', err)
      } finally {
        setLoadingReports(false)
      }
    }

    fetchReports()
  }, [])

  const loadReport = async (reportId: number) => {
    setLoadingDetail(true)
    try {
      const result = await getReportDetail(reportId)
      setSelectedReport(result)
    } catch (err) {
      console.error('Failed to load report:', err)
    } finally {
      setLoadingDetail(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const result = await generateReport(reportType)
      setSelectedReport(result)
      const updated = await getReports()
      setReports(updated)
    } catch (err) {
      console.error('Failed to generate report:', err)
    } finally {
      setGenerating(false)
    }
  }

  const radarOption = useMemo(() => {
    if (!selectedReport) return {}

    return {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(var(--bg-card-rgb), 0.95)',
        borderColor: 'rgba(var(--border-default-rgb), 0.5)',
        textStyle: { color: 'rgba(var(--text-primary-rgb), 1)' },
      },
      radar: {
        indicator: [
          { name: '学业', max: 100 },
          { name: '身体', max: 100 },
          { name: '心理', max: 100 },
          { name: '社交', max: 100 },
        ],
        axisName: { color: 'rgba(var(--text-muted-rgb), 1)' },
        splitLine: { lineStyle: { color: 'rgba(var(--border-default-rgb), 0.4)' } },
        splitArea: {
          areaStyle: {
            color: ['rgba(var(--bg-card-rgb), 1)', 'rgba(var(--bg-active-rgb), 0.3)'],
          },
        },
        axisLine: { lineStyle: { color: 'rgba(var(--border-default-rgb), 0.4)' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [
                selectedReport.academic_score,
                selectedReport.physical_score,
                selectedReport.mental_score,
                selectedReport.social_score,
              ],
              name: '健康度',
              lineStyle: { color: 'rgba(var(--accent-primary-rgb), 1)', width: 2 },
              areaStyle: {
                color: 'rgba(var(--accent-primary-rgb), 0.3)',
              },
              itemStyle: { color: 'rgba(var(--accent-primary-rgb), 1)' },
            },
          ],
        },
      ],
    }
  }, [selectedReport])

  const stats = useMemo(() => {
    if (!selectedReport) return []
    return [
      { label: '总学习时长', value: `${selectedReport.total_study_hours.toFixed(1)} 小时`, icon: '⏱️', color: 'text-accent-primary' },
      { label: '任务完成率', value: `${(selectedReport.task_completion_rate * 100).toFixed(0)}%`, icon: '✅', color: 'text-success' },
      { label: '平均专注度', value: selectedReport.avg_focus_score.toFixed(0), icon: '🎯', color: 'text-warning' },
      { label: '活跃天数', value: `${selectedReport.active_days} 天`, icon: '🔥', color: 'text-danger' },
    ]
  }, [selectedReport])

  const reportTypes = ['weekly', 'monthly', 'semester']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">📊</span>
          成长档案
        </h1>
        <p className="text-text-muted mt-1">记录你的成长轨迹，生成个性化成长报告</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>生成报告</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-1 bg-bg-active rounded-lg p-1">
                {reportTypes.map(type => {
                  const info = reportTypeMap[type]
                  return (
                    <button
                      key={type}
                      onClick={() => setReportType(type)}
                      className={`flex-1 py-2 px-2 text-sm font-medium rounded-md transition-all ${
                        reportType === type
                          ? 'bg-bg-card text-text-primary shadow-sm'
                          : 'text-text-muted hover:text-text-secondary'
                      }`}
                    >
                      {info.label}
                    </button>
                  )
                })}
              </div>
              <Button
                variant="primary"
                className="w-full"
                onClick={handleGenerate}
                isLoading={generating}
              >
                {generating ? '生成中...' : '生成报告'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>历史报告</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingReports ? (
                <div className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-16 bg-bg-active rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : reports.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {reports.map(report => {
                    const typeInfo = reportTypeMap[report.report_type] || { label: report.report_type, icon: '📄' }
                    return (
                      <div
                        key={report.id}
                        onClick={() => loadReport(report.id)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          selectedReport?.id === report.id
                            ? 'bg-accent-primary/10 border-accent-primary'
                            : 'bg-bg-card border-border-default hover:border-accent-primary/50'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span>{typeInfo.icon}</span>
                          <span className="font-medium text-text-primary text-sm">
                            {report.title || typeInfo.label}
                          </span>
                        </div>
                        <p className="text-xs text-text-muted">
                          {report.period_start} ~ {report.period_end}
                        </p>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-text-muted">
                  <span className="text-3xl mb-2 block">📝</span>
                  <p className="text-sm">暂无历史报告</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-3">
          {loadingDetail ? (
            <Card className="h-full min-h-96">
              <CardContent className="animate-pulse" />
            </Card>
          ) : selectedReport ? (
            <div className="space-y-6">
              <Card className="bg-gradient-to-br from-accent-primary/10 via-bg-card to-bg-card">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-text-primary">
                        {selectedReport.title}
                      </h2>
                      <p className="text-text-muted text-sm mt-1">
                        {selectedReport.period_start} ~ {selectedReport.period_end}
                      </p>
                    </div>
                    <Badge variant="accent">
                      综合评分 {selectedReport.overall_score.toFixed(0)}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {stats.map((stat, idx) => (
                    <Card key={idx}>
                      <CardContent className="pt-6">
                        <div className="text-2xl mb-2">{stat.icon}</div>
                        <p className="text-text-muted text-sm">{stat.label}</p>
                        <p className={`text-2xl font-bold mt-1 ${stat.color}`}>
                          {stat.value}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>四维度健康度</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ReactECharts
                      option={radarOption}
                      style={{ height: 280 }}
                      theme="light"
                      notMerge={true}
                      lazyUpdate={true}
                    />
                  </CardContent>
                </Card>

                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <span>🌟</span> 亮点
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {selectedReport.highlights.length > 0 ? (
                          selectedReport.highlights.map((h, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                              <span className="text-success mt-0.5">✓</span>
                              {h}
                            </li>
                          ))
                        ) : (
                          <p className="text-text-muted text-sm">继续加油，期待你的亮点！</p>
                        )}
                      </ul>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <span>💡</span> 改进建议
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {selectedReport.suggestions.length > 0 ? (
                          selectedReport.suggestions.map((s, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                              <span className="text-warning mt-0.5">!</span>
                              {s}
                            </li>
                          ))
                        ) : (
                          <p className="text-text-muted text-sm">保持现状，你做得很好！</p>
                        )}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          ) : (
            <Card className="h-full min-h-96">
              <CardContent className="flex flex-col items-center justify-center h-96 text-text-muted">
                <span className="text-6xl mb-4">📄</span>
                <p className="font-medium text-text-secondary">选择或生成一份报告</p>
                <p className="text-sm mt-1">从左侧选择历史报告，或生成新的报告</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

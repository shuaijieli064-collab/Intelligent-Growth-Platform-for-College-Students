import { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Tabs, Tab } from '@/components/ui/Tabs'
import ReactECharts from 'echarts-for-react'
import { useEchartsTheme } from '@/hooks/useEchartsTheme'
import { escapeHtml } from '@/utils/safe'
import {
  getStudyCurve,
  getHealthTrend,
  getGradeRadar,
  getKnowledgeHeatmap,
  type StudyCurveData,
  type HealthTrendData,
  type GradeRadarData,
  type KnowledgeHeatmapData,
} from '@/api/visualization'

export default function VisualizationPage() {
  const { isDark, colors, mergeOption } = useEchartsTheme()
  const [studyCurve, setStudyCurve] = useState<StudyCurveData | null>(null)
  const [healthTrend, setHealthTrend] = useState<HealthTrendData | null>(null)
  const [gradeRadar, setGradeRadar] = useState<GradeRadarData | null>(null)
  const [knowledgeHeatmap, setKnowledgeHeatmap] = useState<KnowledgeHeatmapData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true)
      try {
        const [curve, health, radar, heatmap] = await Promise.all([
          getStudyCurve(),
          getHealthTrend(),
          getGradeRadar(),
          getKnowledgeHeatmap(),
        ])
        setStudyCurve(curve)
        setHealthTrend(health)
        setGradeRadar(radar)
        setKnowledgeHeatmap(heatmap)
      } catch (err) {
        console.error('Failed to fetch visualization data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [])

  const studyCurveOption = useMemo(() => {
    if (!studyCurve?.data?.length) return {}

    const dates = studyCurve.data.map(d => d.date.slice(5))
    const studyMinutes = studyCurve.data.map(d => d.study_minutes)
    const avg7day = studyCurve.data.map(d => d.avg_7day)
    const focusScore = studyCurve.data.map(d => d.focus_score || 0)

    return mergeOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      legend: {
        data: ['学习时长', '7日均值', '专注度'],
        top: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 40, containLabel: true },
      xAxis: {
        type: 'category',
        data: dates,
      },
      yAxis: [
        {
          type: 'value',
          name: '分钟',
        },
        {
          type: 'value',
          name: '专注度',
          min: 0,
          max: 100,
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: '学习时长',
          type: 'bar',
          data: studyMinutes,
          itemStyle: {
            color: colors.primary + '99',
            borderRadius: [4, 4, 0, 0],
          },
        },
        {
          name: '7日均值',
          type: 'line',
          smooth: true,
          data: avg7day,
          lineStyle: { color: colors.success, width: 2 },
          itemStyle: { color: colors.success },
          symbol: 'none',
        },
        {
          name: '专注度',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: focusScore,
          lineStyle: { color: colors.warning, width: 2, type: 'dashed' },
          itemStyle: { color: colors.warning },
          symbol: 'circle',
          symbolSize: 4,
        },
      ],
    })
  }, [studyCurve, isDark, colors, mergeOption])

  const healthTrendOption = useMemo(() => {
    if (!healthTrend?.data?.length) return {}

    // 接口按日期倒序返回，反转为时间正序
    const rows = [...healthTrend.data].reverse()
    const dates = rows.map(d => d.date.slice(5))

    return mergeOption({
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        data: ['综合', '学业', '身体', '心理', '社交'],
        top: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 40, containLabel: true },
      xAxis: {
        type: 'category',
        data: dates,
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
      },
      series: [
        {
          name: '综合',
          type: 'line',
          smooth: true,
          data: rows.map(d => d.overall),
          lineStyle: { color: colors.primary, width: 3 },
          itemStyle: { color: colors.primary },
          symbol: 'circle',
          symbolSize: 5,
        },
        {
          name: '学业',
          type: 'line',
          smooth: true,
          data: rows.map(d => d.academic),
          lineStyle: { color: colors.success, width: 2 },
          itemStyle: { color: colors.success },
          symbol: 'circle',
          symbolSize: 4,
        },
        {
          name: '身体',
          type: 'line',
          smooth: true,
          data: rows.map(d => d.physical),
          lineStyle: { color: colors.warning, width: 2 },
          itemStyle: { color: colors.warning },
          symbol: 'circle',
          symbolSize: 4,
        },
        {
          name: '心理',
          type: 'line',
          smooth: true,
          data: rows.map(d => d.mental),
          lineStyle: { color: colors.purple, width: 2 },
          itemStyle: { color: colors.purple },
          symbol: 'circle',
          symbolSize: 4,
        },
        {
          name: '社交',
          type: 'line',
          smooth: true,
          data: rows.map(d => d.social),
          lineStyle: { color: colors.danger, width: 2 },
          itemStyle: { color: colors.danger },
          symbol: 'circle',
          symbolSize: 4,
        },
      ],
    })
  }, [healthTrend, isDark, colors, mergeOption])

  const gradeRadarOption = useMemo(() => {
    if (!gradeRadar?.courses?.length) return {}

    return mergeOption({
      tooltip: {
        trigger: 'item',
      },
      radar: {
        indicator: gradeRadar.courses.map(c => ({ name: c.course_name, max: 100 })),
        axisName: { fontSize: 11 },
        splitLine: { lineStyle: { color: isDark ? 'rgba(61, 62, 66, 0.4)' : 'rgba(232, 229, 225, 0.4)' } },
        splitArea: {
          areaStyle: {
            color: isDark ? ['rgba(33, 34, 38, 1)', 'rgba(37, 38, 41, 0.3)'] : ['rgba(255, 255, 255, 1)', 'rgba(243, 241, 237, 0.3)'],
          },
        },
        axisLine: { lineStyle: { color: isDark ? 'rgba(61, 62, 66, 0.4)' : 'rgba(232, 229, 225, 0.4)' } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: gradeRadar.courses.map(c => c.score),
              name: '成绩',
              lineStyle: { color: colors.primary, width: 2 },
              areaStyle: { color: colors.primary + '4d' },
              itemStyle: { color: colors.primary },
            },
          ],
        },
      ],
    })
  }, [gradeRadar, isDark, colors, mergeOption])

  const heatmapOption = useMemo(() => {
    if (!knowledgeHeatmap?.courses?.length || !knowledgeHeatmap?.kps?.length) return {}

    const data = knowledgeHeatmap.data.map(d => [
      knowledgeHeatmap.kps.indexOf(d.kp_name),
      knowledgeHeatmap.courses.indexOf(d.course_name),
      d.mastery,
    ])

    return mergeOption({
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          const course = knowledgeHeatmap.courses[params.data[1]]
          const kp = knowledgeHeatmap.kps[params.data[0]]
          const value = params.data[2]
          return `${escapeHtml(course)}<br/>${escapeHtml(kp)}<br/>掌握度: ${Number(value).toFixed(0)}%`
        },
      },
      grid: { left: 100, right: 40, top: 20, bottom: 80 },
      xAxis: {
        type: 'category',
        data: knowledgeHeatmap.kps,
        axisLabel: {
          rotate: 45,
          fontSize: 10,
          interval: 0,
        },
        splitArea: { show: true },
      },
      yAxis: {
        type: 'category',
        data: knowledgeHeatmap.courses,
        splitArea: { show: true },
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
            colors.danger + '66',
            colors.warning + 'b3',
            colors.success,
          ],
        },
      },
      series: [
        {
          name: '掌握度',
          type: 'heatmap',
          data: data,
          label: {
            show: true,
            fontSize: 10,
            formatter: (params: any) => params.data[2].toFixed(0),
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    })
  }, [knowledgeHeatmap, isDark, colors, mergeOption])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">📈</span>
          数据可视化
        </h1>
        <p className="text-text-muted mt-1">多维度数据洞察，全面了解学习状态</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="h-96 bg-bg-active rounded-xl animate-pulse" />
          ) : (
            <Tabs defaultValue="study-curve">
              <Tab value="study-curve" label="学习曲线">
                <Card className="border-0 shadow-none">
                  <CardHeader>
                    <CardTitle>学习曲线</CardTitle>
                    <CardDescription>30天学习时长、7日移动均线与专注度对比</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ReactECharts
                      option={studyCurveOption}
                      style={{ height: 400 }}
                      notMerge={true}
                      lazyUpdate={true}
                    />
                  </CardContent>
                </Card>
              </Tab>

              <Tab value="health-trend" label="健康趋势">
                <Card className="border-0 shadow-none">
                  <CardHeader>
                    <CardTitle>健康趋势</CardTitle>
                    <CardDescription>四维度健康度历史变化趋势</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {healthTrend?.data?.length ? (
                      <ReactECharts
                        option={healthTrendOption}
                        style={{ height: 400 }}
                        notMerge={true}
                        lazyUpdate={true}
                      />
                    ) : (
                      <div className="h-80 flex items-center justify-center text-text-muted">
                        <div className="text-center">
                          <span className="text-4xl mb-2 block">📈</span>
                          <p>暂无健康趋势数据，完善健康打卡后自动生成</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Tab>

              <Tab value="grade-radar" label="成绩雷达">
                <Card className="border-0 shadow-none">
                  <CardHeader>
                    <CardTitle>成绩雷达</CardTitle>
                    <CardDescription>各课程成绩对比分析</CardDescription>
                  </CardHeader>
                  <CardContent className="flex justify-center">
                    {gradeRadar?.courses?.length ? (
                      <ReactECharts
                        option={gradeRadarOption}
                        style={{ height: 400, width: '100%', maxWidth: 600 }}
                        notMerge={true}
                        lazyUpdate={true}
                      />
                    ) : (
                      <div className="h-80 flex items-center justify-center text-text-muted">
                        <div className="text-center">
                          <span className="text-4xl mb-2 block">🎯</span>
                          <p>暂无成绩数据，录入成绩后自动生成</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Tab>

              <Tab value="knowledge-heatmap" label="知识热力图">
                <Card className="border-0 shadow-none">
                  <CardHeader>
                    <CardTitle>知识热力图</CardTitle>
                    <CardDescription>课程×知识点掌握度热力分布</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {knowledgeHeatmap?.kps?.length ? (
                      <ReactECharts
                        option={heatmapOption}
                        style={{ height: 400 }}
                        notMerge={true}
                        lazyUpdate={true}
                      />
                    ) : (
                      <div className="h-80 flex items-center justify-center text-text-muted">
                        <div className="text-center">
                          <span className="text-4xl mb-2 block">🔍</span>
                          <p>暂无知识图谱数据</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Tab>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

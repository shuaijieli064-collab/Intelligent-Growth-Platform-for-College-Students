import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Progress } from '@/components/ui/Progress'
import { Badge } from '@/components/ui/Badge'
import { getCoursesWithScores, type CourseWithScores } from '@/api/gradePredict'
import {
  getStudyPlan,
  generatePlan,
  updateTask,
  completeNextTask,
  type StudyPlan,
  type StudyPlanTask,
} from '@/api/studyPlan'

const taskTypeMap: Record<string, { label: string; icon: string; color: string }> = {
  review: { label: '基础学习', icon: '📖', color: 'bg-accent-light text-accent-text' },
  practice: { label: '专项练习', icon: '✏️', color: 'bg-warning/10 text-warning' },
  mock_exam: { label: '模拟考试', icon: '📝', color: 'bg-danger/10 text-danger' },
  summarize: { label: '总结归纳', icon: '🗂️', color: 'bg-blue-500/10 text-blue-500' },
  memorize: { label: '背诵记忆', icon: '🧠', color: 'bg-purple-500/10 text-purple-500' },
}

const priorityMap: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  high: { label: '高', variant: 'danger' },
  medium: { label: '中', variant: 'warning' },
  low: { label: '低', variant: 'success' },
}

function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  return (
    <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg ${
      type === 'success' ? 'bg-success text-white' : 'bg-danger text-white'
    }`}>
      {message}
      <button type="button" className="ml-3 opacity-80 hover:opacity-100" onClick={onClose}>×</button>
    </div>
  )
}

export default function StudyPlanPage() {
  const [courses, setCourses] = useState<CourseWithScores[]>([])
  const [plan, setPlan] = useState<StudyPlan | null>(null)
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null)
  const [goalScore, setGoalScore] = useState<string>('85')
  const [dailyMinutes, setDailyMinutes] = useState<string>('90')
  const [examDate, setExamDate] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [taskUpdating, setTaskUpdating] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const result = await getCoursesWithScores()
        setCourses(result)
        if (result.length > 0) {
          setSelectedCourse(result[0].course_id)
        }
      } catch (err) {
        console.error('Failed to fetch courses:', err)
      }
    }

    fetchCourses()
  }, [])

  useEffect(() => {
    const fetchPlan = async () => {
      setLoading(true)
      try {
        const result = await getStudyPlan()
        setPlan(result)
      } catch (err) {
        console.error('Failed to fetch study plan:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPlan()
  }, [])

  useEffect(() => {
    const date = new Date()
    date.setDate(date.getDate() + 30)
    setExamDate(date.toISOString().split('T')[0])
  }, [])

  const handleGenerate = async () => {
    if (!selectedCourse) return

    const course = courses.find(c => c.course_id === selectedCourse)
    if (!course) return

    setGenerating(true)
    try {
      const result = await generatePlan({
        subject: course.course_name,
        course_id: selectedCourse,
        goal_score: parseFloat(goalScore),
        exam_date: examDate,
        daily_minutes: parseInt(dailyMinutes) || 90,
      })
      setPlan(result)
      setToast({ message: '学习计划已生成', type: 'success' })
    } catch (err) {
      console.error('Failed to generate plan:', err)
      const detail = (err as { message?: string })?.message
      setToast({ message: detail || '生成计划失败，请稍后重试', type: 'error' })
    } finally {
      setGenerating(false)
    }
  }

  const handleToggleTask = async (index: number, done: boolean) => {
    if (!plan) return

    setTaskUpdating(true)
    try {
      const result = await updateTask(index, done)
      const newTasks = [...plan.plan_content]
      newTasks[index] = { ...newTasks[index], done }
      setPlan({
        ...plan,
        plan_content: newTasks,
        progress: result.progress ?? plan.progress,
      })
    } catch (err) {
      console.error('Failed to update task:', err)
      const detail = (err as { message?: string })?.message
      setToast({ message: detail || '任务更新失败', type: 'error' })
    } finally {
      setTaskUpdating(false)
    }
  }

  const handleNextTask = async () => {
    if (!plan) return

    setTaskUpdating(true)
    try {
      const result = await completeNextTask()
      const newTasks = [...plan.plan_content]
      if (result.task_index != null && result.task_index >= 0 && result.task_index < newTasks.length) {
        newTasks[result.task_index] = { ...newTasks[result.task_index], done: true }
      }
      setPlan({
        ...plan,
        plan_content: newTasks,
        progress: result.progress ?? plan.progress,
      })
    } catch (err) {
      console.error('Failed to complete next task:', err)
      const detail = (err as { message?: string })?.message
      setToast({ message: detail || '操作失败，请稍后重试', type: 'error' })
    } finally {
      setTaskUpdating(false)
    }
  }

  const getDailyTasks = (tasks: StudyPlanTask[]) => {
    const grouped = new Map<number, { task: StudyPlanTask; index: number }[]>()
    tasks.forEach((task, index) => {
      if (!grouped.has(task.day)) grouped.set(task.day, [])
      grouped.get(task.day)!.push({ task, index })
    })
    return Array.from(grouped.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([day, dayTasks]) => ({ day, tasks: dayTasks }))
  }

  const dailyPlans = plan ? getDailyTasks(plan.plan_content) : []
  const completedCount = plan?.plan_content.filter(t => t.done).length || 0
  const totalCount = plan?.plan_content.length || 0

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">📋</span>
          学习计划
        </h1>
        <p className="text-text-muted mt-1">智能生成个性化学习计划，高效备考</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>生成学习计划</CardTitle>
            <CardDescription>根据薄弱点智能规划</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select
              label="选择课程"
              value={selectedCourse ?? ''}
              onChange={(e) => setSelectedCourse(e.target.value ? parseInt(e.target.value) : null)}
            >
              {courses.map(course => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_name}
                </option>
              ))}
            </Select>

            <Input
              label="目标分数"
              type="number"
              min={0}
              max={100}
              value={goalScore}
              onChange={(e) => setGoalScore(e.target.value)}
            />

            <Select
              label="每日学习时长"
              value={dailyMinutes}
              onChange={(e) => setDailyMinutes(e.target.value)}
            >
              <option value="30">30 分钟（轻度）</option>
              <option value="60">60 分钟（适中）</option>
              <option value="90">90 分钟（推荐）</option>
              <option value="120">120 分钟（强化）</option>
              <option value="180">180 分钟（冲刺）</option>
            </Select>

            <Input
              label="考试日期"
              type="date"
              value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
            />

            <Button
              variant="primary"
              onClick={handleGenerate}
              isLoading={generating}
              className="w-full"
              disabled={!selectedCourse || !examDate}
            >
              {generating ? '生成中...' : '生成学习计划'}
            </Button>

            {plan && (
              <div className="pt-4 border-t border-border-default space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-text-muted">总体进度</span>
                    <span className="font-medium text-text-primary">
                      {completedCount}/{totalCount} ({plan.progress.toFixed(1)}%)
                    </span>
                  </div>
                  <Progress value={plan.progress} variant="success" />
                </div>

                <Button
                  variant="success"
                  onClick={handleNextTask}
                  isLoading={taskUpdating}
                  className="w-full"
                  disabled={completedCount === totalCount}
                >
                  {completedCount === totalCount ? '🎉 全部完成' : '✅ 完成下个任务'}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {plan ? plan.subject : '学习计划'}
                </CardTitle>
                <CardDescription>
                  {plan ? `目标分数: ${plan.goal_score} 分 | 考试日期: ${plan.exam_date}` : '生成计划后查看详情'}
                </CardDescription>
              </div>
              {plan && (
                <Badge variant={plan.status === 'active' ? 'success' : 'default'}>
                  {plan.status === 'active' ? '进行中' : plan.status}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-bg-active rounded-lg animate-pulse" />
                ))}
              </div>
            ) : plan && plan.plan_content.length > 0 ? (
              <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                {dailyPlans.map((dayPlan, idx) => {
                  const dayTotal = dayPlan.tasks.reduce((s, t) => s + (t.task.duration_min || 0), 0)
                  const dayDone = dayPlan.tasks.filter(t => t.task.done).length
                  const allDone = dayDone === dayPlan.tasks.length
                  return (
                    <div
                      key={dayPlan.day}
                      className={`rounded-xl border transition-colors ${
                        allDone
                          ? 'border-success/30 bg-success/5'
                          : idx === 0
                            ? 'border-accent-primary/50 bg-accent-primary/5'
                            : 'border-border-default'
                      }`}
                    >
                      <div className="flex items-center justify-between px-4 py-3 border-b border-border-default/60">
                        <div className="flex items-center gap-3">
                          <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold ${
                            allDone ? 'bg-success text-white' : 'bg-accent-primary text-white'
                          }`}>
                            {dayPlan.day}
                          </span>
                          <div>
                            <p className="text-sm font-semibold text-text-primary">第 {dayPlan.day} 天</p>
                            <p className="text-xs text-text-muted">
                              {dayPlan.tasks.length} 个任务 · 约 {dayTotal} 分钟
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {allDone && <Badge variant="success" size="sm">✓ 已完成</Badge>}
                          <span className="text-xs text-text-muted">{dayDone}/{dayPlan.tasks.length}</span>
                        </div>
                      </div>
                      <div className="p-3 space-y-2">
                        {dayPlan.tasks.map(({ task, index }) => {
                          const taskInfo = taskTypeMap[task.type] || { label: task.type, icon: '📌', color: 'bg-bg-hover text-text-secondary' }
                          const priorityInfo = priorityMap[task.priority] || { label: task.priority, variant: 'default' as const }

                          return (
                            <div
                              key={index}
                              className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                                task.done ? 'bg-success/10 opacity-70' : 'bg-bg-hover/40 hover:bg-bg-hover/70'
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={task.done}
                                onChange={(e) => handleToggleTask(index, e.target.checked)}
                                className="mt-1 w-4 h-4 rounded border-border-default text-accent-primary focus:ring-accent-primary/20"
                                disabled={taskUpdating}
                              />
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className={`text-sm ${task.done ? 'line-through text-text-muted' : 'text-text-primary font-medium'}`}>
                                    {task.task}
                                  </span>
                                  <span className={`px-2 py-0.5 rounded text-xs ${taskInfo.color}`}>
                                    {taskInfo.icon} {taskInfo.label}
                                  </span>
                                  <Badge variant={priorityInfo.variant} size="sm">
                                    {priorityInfo.label}优先级
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-4 mt-1 text-xs text-text-muted">
                                  <span>⏱ {task.duration_min} 分钟</span>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-16 text-text-muted">
                <span className="text-5xl mb-4 block">📅</span>
                <p className="font-medium text-text-secondary">暂无学习计划</p>
                <p className="text-sm mt-1">填写表单生成你的专属学习计划</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

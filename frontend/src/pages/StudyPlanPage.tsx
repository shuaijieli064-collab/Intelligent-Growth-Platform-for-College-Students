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
  review: { label: '复习', icon: '📖', color: 'bg-accent-light text-accent-text' },
  practice: { label: '练习', icon: '✏️', color: 'bg-warning/10 text-warning' },
  mock_exam: { label: '模拟考试', icon: '📝', color: 'bg-danger/10 text-danger' },
}

const priorityMap: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  high: { label: '高', variant: 'danger' },
  medium: { label: '中', variant: 'warning' },
  low: { label: '低', variant: 'success' },
}

export default function StudyPlanPage() {
  const [courses, setCourses] = useState<CourseWithScores[]>([])
  const [plan, setPlan] = useState<StudyPlan | null>(null)
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null)
  const [goalScore, setGoalScore] = useState<string>('85')
  const [examDate, setExamDate] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [taskUpdating, setTaskUpdating] = useState(false)

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
      })
      setPlan(result)
    } catch (err) {
      console.error('Failed to generate plan:', err)
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
        progress: result.progress,
      })
    } catch (err) {
      console.error('Failed to update task:', err)
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
      if (result.task_index >= 0) {
        newTasks[result.task_index] = { ...newTasks[result.task_index], done: true }
      }
      setPlan({
        ...plan,
        plan_content: newTasks,
        progress: result.progress,
      })
    } catch (err) {
      console.error('Failed to complete next task:', err)
    } finally {
      setTaskUpdating(false)
    }
  }

  const getPhaseTasks = (tasks: StudyPlanTask[]) => {
    const phases: { name: string; tasks: StudyPlanTask[] }[] = [
      { name: '第一阶段：基础知识补强', tasks: [] },
      { name: '第二阶段：综合练习', tasks: [] },
      { name: '第三阶段：模拟考试', tasks: [] },
      { name: '第四阶段：最终复习', tasks: [] },
    ]

    tasks.forEach(task => {
      if (task.type === 'review' && task.task.includes('强化')) {
        phases[0].tasks.push(task)
      } else if (task.type === 'practice') {
        phases[1].tasks.push(task)
      } else if (task.type === 'mock_exam') {
        phases[2].tasks.push(task)
      } else {
        phases[3].tasks.push(task)
      }
    })

    return phases.filter(p => p.tasks.length > 0)
  }

  const phases = plan ? getPhaseTasks(plan.plan_content) : []
  const completedCount = plan?.plan_content.filter(t => t.done).length || 0
  const totalCount = plan?.plan_content.length || 0

  return (
    <div className="space-y-6">
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
              <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2">
                {phases.map((phase, phaseIndex) => (
                  <div key={phaseIndex}>
                    <h4 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-accent-primary text-white text-xs flex items-center justify-center">
                        {phaseIndex + 1}
                      </span>
                      {phase.name}
                    </h4>
                    <div className="space-y-2 ml-8">
                      {phase.tasks.map((task) => {
                        const taskIndex = plan.plan_content.findIndex(
                          t => t.task === task.task && t.day === task.day
                        )
                        const taskInfo = taskTypeMap[task.type] || { label: task.type, icon: '📌', color: 'bg-bg-hover text-text-secondary' }
                        const priorityInfo = priorityMap[task.priority] || { label: task.priority, variant: 'default' as const }

                        return (
                          <div
                            key={taskIndex}
                            className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                              task.done ? 'bg-success/5 opacity-70' : 'bg-bg-hover/30 hover:bg-bg-hover/50'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={task.done}
                              onChange={(e) => handleToggleTask(taskIndex, e.target.checked)}
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
                                <span>第 {task.day} 天</span>
                                <span>{task.duration_min} 分钟</span>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
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

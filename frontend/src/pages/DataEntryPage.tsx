import { useState, useEffect, useRef } from 'react'
import { Tabs, Tab } from '@/components/ui/Tabs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'
import { useAuthStore } from '@/store/authStore'
import {
  getStudyRecords,
  createStudyRecord,
  deleteStudyRecord,
  deleteAllStudyRecords,
  type StudyRecord,
} from '@/api/studyRecord'
import {
  getScores,
  createOrUpdateScore,
  deleteScore,
  type Score,
} from '@/api/score'
import {
  getPhysicalHealth,
  createPhysicalHealth,
  deletePhysicalHealth,
  getMentalHealth,
  createMentalHealth,
  deleteMentalHealth,
  getSocialHealth,
  createSocialHealth,
  deleteSocialHealth,
  type PhysicalHealthRecord,
  type MentalHealthRecord,
  type SocialHealthRecord,
} from '@/api/health'
import {
  getCourses,
  createCourse,
  deleteCourse,
  type Course,
} from '@/api/course'
import { getStudentMe, updateStudentMe } from '@/api/student'

const today = new Date().toISOString().split('T')[0]

function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  const onCloseRef = useRef(onClose)
  onCloseRef.current = onClose

  useEffect(() => {
    const timer = setTimeout(() => onCloseRef.current(), 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg animate-fade-in ${
      type === 'success' ? 'bg-success text-white' : 'bg-danger text-white'
    }`}>
      {message}
    </div>
  )
}

function ConfirmDialog({
  open,
  title,
  message,
  onConfirm,
  onCancel,
}: {
  open: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
}) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-bg-card rounded-xl shadow-xl border border-border-default w-full max-w-md mx-4">
        <div className="px-6 py-5 border-b border-border-default">
          <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
        </div>
        <div className="px-6 py-5">
          <p className="text-text-secondary">{message}</p>
        </div>
        <div className="px-6 py-4 border-t border-border-default flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel}>取消</Button>
          <Button variant="danger" onClick={onConfirm}>确认删除</Button>
        </div>
      </div>
    </div>
  )
}

function StudyRecordTab() {
  const [records, setRecords] = useState<StudyRecord[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [confirmClear, setConfirmClear] = useState(false)

  const [form, setForm] = useState({
    study_date: today,
    study_hours: '',
    course_id: '',
    task_completed: '',
    focus_score: '',
    notes: '',
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const [recordsData, coursesData] = await Promise.all([
        getStudyRecords(),
        getCourses(),
      ])
      setRecords(recordsData)
      setCourses(coursesData)
    } catch (err) {
      console.error('Failed to fetch study records:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.study_hours.trim()) {
      setToast({ message: '请填写学习时长', type: 'error' })
      return
    }
    const hours = parseFloat(form.study_hours)
    if (isNaN(hours) || hours < 0) {
      setToast({ message: '学习时长格式不正确', type: 'error' })
      return
    }
    const focusVal = form.focus_score.trim()
    setSubmitting(true)
    try {
      await createStudyRecord({
        study_date: form.study_date,
        study_hours: hours,
        course_id: form.course_id ? parseInt(form.course_id) : null,
        task_completed: form.task_completed.trim() ? parseInt(form.task_completed) : 0,
        focus_score: focusVal !== '' ? parseInt(focusVal) : null,
        notes: form.notes.trim() || null,
      })
      setToast({ message: '学习记录保存成功', type: 'success' })
      setForm({
        study_date: today,
        study_hours: '',
        course_id: '',
        task_completed: '',
        focus_score: '',
        notes: '',
      })
      fetchData()
    } catch (err) {
      console.error('Failed to create study record:', err)
      setToast({ message: '保存失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (recordId: number) => {
    try {
      await deleteStudyRecord(recordId)
      setToast({ message: '删除成功', type: 'success' })
      fetchData()
    } catch (err) {
      console.error('Failed to delete record:', err)
      setToast({ message: '删除失败', type: 'error' })
    }
  }

  const handleClearAll = async () => {
    try {
      await deleteAllStudyRecords()
      setToast({ message: '已清空全部学习记录', type: 'success' })
      setConfirmClear(false)
      fetchData()
    } catch (err) {
      console.error('Failed to clear records:', err)
      setToast({ message: '清空失败', type: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <ConfirmDialog
        open={confirmClear}
        title="确认清空"
        message="确定要清空全部学习记录吗？此操作不可恢复。"
        onConfirm={handleClearAll}
        onCancel={() => setConfirmClear(false)}
      />

      <Card>
        <CardHeader>
          <CardTitle>录入学习记录</CardTitle>
          <CardDescription>记录每日学习情况，帮助追踪学习进度</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Input
                label="学习日期"
                type="date"
                value={form.study_date}
                onChange={(e) => setForm({ ...form, study_date: e.target.value })}
                required
              />
              <Select
                label="关联课程（可选）"
                value={form.course_id}
                onChange={(e) => setForm({ ...form, course_id: e.target.value })}
              >
                <option value="">不关联</option>
                {courses.map((c) => (
                  <option key={c.course_id} value={c.course_id}>
                    {c.course_name}
                  </option>
                ))}
              </Select>
              <Input
                label="学习时长（小时）"
                type="number"
                min="0"
                max="24"
                step="0.5"
                placeholder="0-24"
                value={form.study_hours}
                onChange={(e) => setForm({ ...form, study_hours: e.target.value })}
                required
              />
              <Input
                label="完成任务数"
                type="number"
                min="0"
                placeholder="0"
                value={form.task_completed}
                onChange={(e) => setForm({ ...form, task_completed: e.target.value })}
              />
              <Input
                label="专注度（0-100）"
                type="number"
                min="0"
                max="100"
                placeholder="0-100"
                value={form.focus_score}
                onChange={(e) => setForm({ ...form, focus_score: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">备注</label>
              <textarea
                className="w-full px-4 py-2.5 rounded-lg bg-bg-input text-text-primary border border-border-default transition-all duration-200 focus:outline-none focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20"
                rows={3}
                placeholder="记录学习心得或注意事项..."
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>保存记录</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>最近学习记录</CardTitle>
              <CardDescription>最近 30 天的学习记录</CardDescription>
            </div>
            <Button variant="danger" size="sm" onClick={() => setConfirmClear(true)} disabled={records.length === 0}>
              清空全部
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : records.length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无学习记录</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>日期</TableHead>
                  <TableHead>课程</TableHead>
                  <TableHead>学习时长</TableHead>
                  <TableHead>完成任务</TableHead>
                  <TableHead>专注度</TableHead>
                  <TableHead>备注</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((record) => (
                  <TableRow key={record.record_id}>
                    <TableCell>{record.study_date?.toString().split('T')[0]}</TableCell>
                    <TableCell>{record.course_name || '-'}</TableCell>
                    <TableCell>{record.study_hours} 小时</TableCell>
                    <TableCell>{record.task_completed} 个</TableCell>
                    <TableCell>{record.focus_score ?? '-'}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{record.notes || '-'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(record.record_id!)}>
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function ScoreTab() {
  const [scores, setScores] = useState<Score[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [form, setForm] = useState({
    course_id: '',
    usual_score: '',
    midterm_score: '',
    final_score: '',
    has_final_exam: false,
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const [scoresData, coursesData] = await Promise.all([
        getScores(),
        getCourses(),
      ])
      setScores(scoresData)
      setCourses(coursesData)
    } catch (err) {
      console.error('Failed to fetch scores:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.course_id) {
      setToast({ message: '请选择课程', type: 'error' })
      return
    }
    const usualVal = form.usual_score.trim()
    const midtermVal = form.midterm_score.trim()
    const finalVal = form.final_score.trim()
    const hasAnyScore = usualVal !== '' || midtermVal !== '' || (form.has_final_exam && finalVal !== '')
    if (!hasAnyScore) {
      setToast({ message: '请至少填写一项成绩', type: 'error' })
      return
    }
    setSubmitting(true)
    try {
      await createOrUpdateScore({
        course_id: parseInt(form.course_id),
        usual_score: usualVal !== '' ? parseFloat(usualVal) : null,
        midterm_score: midtermVal !== '' ? parseFloat(midtermVal) : null,
        final_score: form.has_final_exam && finalVal !== '' ? parseFloat(finalVal) : null,
        has_final_exam: form.has_final_exam,
      })
      setToast({ message: '成绩保存成功', type: 'success' })
      setForm({
        course_id: '',
        usual_score: '',
        midterm_score: '',
        final_score: '',
        has_final_exam: false,
      })
      fetchData()
    } catch (err) {
      console.error('Failed to save score:', err)
      setToast({ message: '保存失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (scId: number) => {
    try {
      await deleteScore(scId)
      setToast({ message: '删除成功', type: 'success' })
      fetchData()
    } catch (err) {
      console.error('Failed to delete score:', err)
      setToast({ message: '删除失败', type: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <Card>
        <CardHeader>
          <CardTitle>录入成绩</CardTitle>
          <CardDescription>录入课程的平时、期中、期末成绩</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Select
                label="选择课程"
                value={form.course_id}
                onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                required
              >
                <option value="">请选择课程</option>
                {courses.map((c) => (
                  <option key={c.course_id} value={c.course_id}>
                    {c.course_name}
                  </option>
                ))}
              </Select>
              <Input
                label="平时成绩"
                type="number"
                min="0"
                max="100"
                step="0.5"
                placeholder="0-100"
                value={form.usual_score}
                onChange={(e) => setForm({ ...form, usual_score: e.target.value })}
              />
              <Input
                label="期中成绩"
                type="number"
                min="0"
                max="100"
                step="0.5"
                placeholder="0-100"
                value={form.midterm_score}
                onChange={(e) => setForm({ ...form, midterm_score: e.target.value })}
              />
              <Input
                label="期末成绩"
                type="number"
                min="0"
                max="100"
                step="0.5"
                placeholder="0-100"
                value={form.final_score}
                onChange={(e) => setForm({ ...form, final_score: e.target.value })}
                disabled={!form.has_final_exam}
              />
              <div className="flex items-end">
                <Switch
                  label="已参加期末考试"
                  checked={form.has_final_exam}
                  onChange={(checked) => setForm({ ...form, has_final_exam: checked })}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>保存成绩</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>历史成绩</CardTitle>
          <CardDescription>已录入的课程成绩列表</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : scores.filter(s => s.usual_score != null || s.midterm_score != null || s.final_score != null).length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无成绩记录</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>课程名称</TableHead>
                  <TableHead>平时成绩</TableHead>
                  <TableHead>期中成绩</TableHead>
                  <TableHead>期末成绩</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scores.filter(s => s.usual_score != null || s.midterm_score != null || s.final_score != null).map((score) => (
                  <TableRow key={score.id}>
                    <TableCell className="font-medium">{score.course_name}</TableCell>
                    <TableCell>{score.usual_score ?? '-'}</TableCell>
                    <TableCell>{score.midterm_score ?? '-'}</TableCell>
                    <TableCell>{score.final_score ?? '-'}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                        score.has_final_exam
                          ? 'bg-success/10 text-success'
                          : 'bg-warning/10 text-warning'
                      }`}>
                        {score.has_final_exam ? '已完成' : '进行中'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(score.id!)}>
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

const exerciseTypes = [
  { value: 'running', label: '跑步' },
  { value: 'ball', label: '球类' },
  { value: 'fitness', label: '健身' },
  { value: 'yoga', label: '瑜伽' },
  { value: 'swimming', label: '游泳' },
  { value: 'cycling', label: '骑行' },
  { value: 'walking', label: '步行' },
  { value: 'other', label: '其他' },
]

const hideStepsTypes = ['swimming', 'yoga', 'fitness']

function PhysicalHealthTab() {
  const [records, setRecords] = useState<PhysicalHealthRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [form, setForm] = useState({
    record_date: today,
    exercise_type: '',
    exercise_duration: '',
    sleep_hours: '',
    steps: '',
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await getPhysicalHealth()
      setRecords(data)
    } catch (err) {
      console.error('Failed to fetch physical health:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const showSteps = !hideStepsTypes.includes(form.exercise_type)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createPhysicalHealth({
        record_date: form.record_date,
        exercise_type: form.exercise_type || null,
        exercise_duration: parseInt(form.exercise_duration) || 0,
        sleep_hours: form.sleep_hours ? parseFloat(form.sleep_hours) : null,
        steps: showSteps && form.steps ? parseInt(form.steps) : 0,
      })
      setToast({ message: '身体健康记录保存成功', type: 'success' })
      setForm({
        record_date: today,
        exercise_type: '',
        exercise_duration: '',
        sleep_hours: '',
        steps: '',
      })
      fetchData()
    } catch (err) {
      console.error('Failed to create physical health record:', err)
      setToast({ message: '保存失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (recordId: number) => {
    try {
      await deletePhysicalHealth(recordId)
      setToast({ message: '删除成功', type: 'success' })
      fetchData()
    } catch (err) {
      console.error('Failed to delete record:', err)
      setToast({ message: '删除失败', type: 'error' })
    }
  }

  const getExerciseLabel = (type: string) => {
    return exerciseTypes.find(t => t.value === type)?.label || type
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <Card>
        <CardHeader>
          <CardTitle>身体健康记录</CardTitle>
          <CardDescription>记录运动、睡眠等身体健康数据</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Input
                label="记录日期"
                type="date"
                value={form.record_date}
                onChange={(e) => setForm({ ...form, record_date: e.target.value })}
                required
              />
              <Select
                label="运动类型"
                value={form.exercise_type}
                onChange={(e) => setForm({ ...form, exercise_type: e.target.value })}
              >
                <option value="">请选择</option>
                {exerciseTypes.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </Select>
              <Input
                label="运动时长（分钟）"
                type="number"
                min="0"
                placeholder="0"
                value={form.exercise_duration}
                onChange={(e) => setForm({ ...form, exercise_duration: e.target.value })}
              />
              <Input
                label="睡眠时长（小时）"
                type="number"
                min="0"
                max="24"
                step="0.5"
                placeholder="0-24"
                value={form.sleep_hours}
                onChange={(e) => setForm({ ...form, sleep_hours: e.target.value })}
              />
              {showSteps && (
                <Input
                  label="步数"
                  type="number"
                  min="0"
                  placeholder="0"
                  value={form.steps}
                  onChange={(e) => setForm({ ...form, steps: e.target.value })}
                />
              )}
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>保存记录</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>最近记录</CardTitle>
          <CardDescription>最近 30 天的身体健康记录</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : records.length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无记录</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>日期</TableHead>
                  <TableHead>运动类型</TableHead>
                  <TableHead>运动时长</TableHead>
                  <TableHead>睡眠时长</TableHead>
                  <TableHead>步数</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>{record.record_date?.toString().split('T')[0]}</TableCell>
                    <TableCell>{record.exercise_type ? getExerciseLabel(record.exercise_type) : '-'}</TableCell>
                    <TableCell>{record.exercise_duration} 分钟</TableCell>
                    <TableCell>{record.sleep_hours ? `${record.sleep_hours} 小时` : '-'}</TableCell>
                    <TableCell>{record.steps > 0 ? record.steps.toLocaleString() : '-'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(record.id!)}>
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function MentalHealthTab() {
  const [records, setRecords] = useState<MentalHealthRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [form, setForm] = useState({
    record_date: today,
    mood_score: '',
    stress_level: '',
    anxiety_level: '',
    notes: '',
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await getMentalHealth()
      setRecords(data)
    } catch (err) {
      console.error('Failed to fetch mental health:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createMentalHealth({
        record_date: form.record_date,
        mood_score: form.mood_score ? parseInt(form.mood_score) : null,
        stress_level: form.stress_level ? parseInt(form.stress_level) : null,
        anxiety_level: form.anxiety_level ? parseInt(form.anxiety_level) : null,
        notes: form.notes || null,
      })
      setToast({ message: '心理健康记录保存成功', type: 'success' })
      setForm({
        record_date: today,
        mood_score: '',
        stress_level: '',
        anxiety_level: '',
        notes: '',
      })
      fetchData()
    } catch (err) {
      console.error('Failed to create mental health record:', err)
      setToast({ message: '保存失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (recordId: number) => {
    try {
      await deleteMentalHealth(recordId)
      setToast({ message: '删除成功', type: 'success' })
      fetchData()
    } catch (err) {
      console.error('Failed to delete record:', err)
      setToast({ message: '删除失败', type: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <Card>
        <CardHeader>
          <CardTitle>心理健康记录</CardTitle>
          <CardDescription>记录心情、压力、焦虑等心理状态</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="记录日期"
                type="date"
                value={form.record_date}
                onChange={(e) => setForm({ ...form, record_date: e.target.value })}
                required
              />
              <Input
                label="心情评分（1-10）"
                type="number"
                min="1"
                max="10"
                placeholder="1-10"
                value={form.mood_score}
                onChange={(e) => setForm({ ...form, mood_score: e.target.value })}
              />
              <Input
                label="压力等级（1-5）"
                type="number"
                min="1"
                max="5"
                placeholder="1-5"
                value={form.stress_level}
                onChange={(e) => setForm({ ...form, stress_level: e.target.value })}
              />
              <Input
                label="焦虑等级（1-5）"
                type="number"
                min="1"
                max="5"
                placeholder="1-5"
                value={form.anxiety_level}
                onChange={(e) => setForm({ ...form, anxiety_level: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">心情日记</label>
              <textarea
                className="w-full px-4 py-2.5 rounded-lg bg-bg-input text-text-primary border border-border-default transition-all duration-200 focus:outline-none focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20"
                rows={4}
                placeholder="记录今天的心情和感受..."
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>保存记录</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>最近记录</CardTitle>
          <CardDescription>最近 30 天的心理健康记录</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : records.length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无记录</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>日期</TableHead>
                  <TableHead>心情评分</TableHead>
                  <TableHead>压力等级</TableHead>
                  <TableHead>焦虑等级</TableHead>
                  <TableHead>心情日记</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>{record.record_date?.toString().split('T')[0]}</TableCell>
                    <TableCell>{record.mood_score ?? '-'}</TableCell>
                    <TableCell>{record.stress_level ?? '-'}</TableCell>
                    <TableCell>{record.anxiety_level ?? '-'}</TableCell>
                    <TableCell className="max-w-[250px] truncate">{record.notes || '-'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(record.id!)}>
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

const activityTypes = [
  { value: 'club', label: '社团' },
  { value: 'party', label: '聚会' },
  { value: 'team', label: '团队项目' },
  { value: 'volunteer', label: '志愿' },
  { value: 'academic', label: '学术交流' },
  { value: 'other', label: '其他' },
]

function SocialHealthTab() {
  const [records, setRecords] = useState<SocialHealthRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [form, setForm] = useState({
    record_date: today,
    activity_type: '',
    duration_minutes: '',
    interaction_count: '',
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await getSocialHealth()
      setRecords(data)
    } catch (err) {
      console.error('Failed to fetch social health:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createSocialHealth({
        record_date: form.record_date,
        activity_type: form.activity_type || null,
        duration_minutes: parseInt(form.duration_minutes) || 0,
        interaction_count: parseInt(form.interaction_count) || 0,
      })
      setToast({ message: '社交健康记录保存成功', type: 'success' })
      setForm({
        record_date: today,
        activity_type: '',
        duration_minutes: '',
        interaction_count: '',
      })
      fetchData()
    } catch (err) {
      console.error('Failed to create social health record:', err)
      setToast({ message: '保存失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (recordId: number) => {
    try {
      await deleteSocialHealth(recordId)
      setToast({ message: '删除成功', type: 'success' })
      fetchData()
    } catch (err) {
      console.error('Failed to delete record:', err)
      setToast({ message: '删除失败', type: 'error' })
    }
  }

  const getActivityLabel = (type: string) => {
    return activityTypes.find(t => t.value === type)?.label || type
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <Card>
        <CardHeader>
          <CardTitle>社交健康记录</CardTitle>
          <CardDescription>记录社交活动和人际互动情况</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="记录日期"
                type="date"
                value={form.record_date}
                onChange={(e) => setForm({ ...form, record_date: e.target.value })}
                required
              />
              <Select
                label="活动类型"
                value={form.activity_type}
                onChange={(e) => setForm({ ...form, activity_type: e.target.value })}
              >
                <option value="">请选择</option>
                {activityTypes.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </Select>
              <Input
                label="活动时长（分钟）"
                type="number"
                min="0"
                placeholder="0"
                value={form.duration_minutes}
                onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
              />
              <Input
                label="互动人数"
                type="number"
                min="0"
                placeholder="0"
                value={form.interaction_count}
                onChange={(e) => setForm({ ...form, interaction_count: e.target.value })}
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>保存记录</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>最近记录</CardTitle>
          <CardDescription>最近 30 天的社交健康记录</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : records.length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无记录</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>日期</TableHead>
                  <TableHead>活动类型</TableHead>
                  <TableHead>活动时长</TableHead>
                  <TableHead>互动人数</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>{record.record_date?.toString().split('T')[0]}</TableCell>
                    <TableCell>{record.activity_type ? getActivityLabel(record.activity_type) : '-'}</TableCell>
                    <TableCell>{record.duration_minutes} 分钟</TableCell>
                    <TableCell>{record.interaction_count} 人</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(record.id!)}>
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function ProfileTab() {
  const { user, fetchUser } = useAuthStore()
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [form, setForm] = useState({
    name: '',
    student_no: '',
    gender: 'M',
    grade_level: '',
    major: '',
    enrollment_year: new Date().getFullYear().toString(),
  })

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true)
      try {
        const student = await getStudentMe()
        setForm({
          name: student.name || user?.name || '',
          student_no: student.student_no || user?.student_no || '',
          gender: student.gender || 'M',
          grade_level: student.grade_level || user?.grade_level || '',
          major: student.major || user?.major || '',
          enrollment_year: student.enrollment_year?.toString() || new Date().getFullYear().toString(),
        })
      } catch (err) {
        console.error('Failed to load profile:', err)
        setToast({ message: '加载个人信息失败', type: 'error' })
      } finally {
        setLoading(false)
      }
    }
    loadProfile()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await updateStudentMe({
        name: form.name,
        student_no: form.student_no,
        gender: form.gender,
        grade_level: form.grade_level,
        major: form.major,
        enrollment_year: parseInt(form.enrollment_year),
      })
      await fetchUser()
      setToast({ message: '个人信息更新成功', type: 'success' })
    } catch (err) {
      console.error('Failed to update profile:', err)
      setToast({ message: '更新失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <Card>
        <CardHeader>
          <CardTitle>个人信息</CardTitle>
          <CardDescription>修改你的个人基本信息</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-8 text-center text-text-muted">加载中...</div>
          ) : (
          <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="姓名"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
              <Input
                label="学号"
                value={form.student_no}
                onChange={(e) => setForm({ ...form, student_no: e.target.value })}
                required
              />
              <Select
                label="性别"
                value={form.gender}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
                required
              >
                <option value="M">男</option>
                <option value="F">女</option>
              </Select>
              <Input
                label="年级"
                placeholder="如：大一、大二"
                value={form.grade_level}
                onChange={(e) => setForm({ ...form, grade_level: e.target.value })}
              />
              <Input
                label="专业"
                placeholder="如：计算机科学与技术"
                value={form.major}
                onChange={(e) => setForm({ ...form, major: e.target.value })}
              />
              <Input
                label="入学年份"
                type="number"
                min="2000"
                max="2099"
                value={form.enrollment_year}
                onChange={(e) => setForm({ ...form, enrollment_year: e.target.value })}
              />
            </div>
            <div className="flex justify-end pt-2">
              <Button type="submit" isLoading={submitting}>保存修改</Button>
            </div>
          </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function CourseTab() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null)

  const [form, setForm] = useState({
    course_code: '',
    course_name: '',
    credit: '',
    semester: '',
    is_compulsory: true,
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await getCourses()
      setCourses(data)
    } catch (err) {
      console.error('Failed to fetch courses:', err)
      setToast({ message: '加载数据失败', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createCourse({
        course_code: form.course_code,
        course_name: form.course_name,
        credit: parseFloat(form.credit) || 0,
        semester: form.semester,
        is_compulsory: form.is_compulsory,
      })
      setToast({ message: '课程添加成功', type: 'success' })
      setForm({
        course_code: '',
        course_name: '',
        credit: '',
        semester: '',
        is_compulsory: true,
      })
      fetchData()
    } catch (err) {
      console.error('Failed to create course:', err)
      setToast({ message: '添加失败，请稍后重试', type: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (courseId: number) => {
    try {
      await deleteCourse(courseId)
      setToast({ message: '课程删除成功', type: 'success' })
      setConfirmDelete(null)
      fetchData()
    } catch (err) {
      console.error('Failed to delete course:', err)
      setToast({ message: '删除失败，请稍后重试', type: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <ConfirmDialog
        open={confirmDelete !== null}
        title="确认删除"
        message="确定要删除这门课程吗？相关的成绩记录也会被删除，此操作不可恢复。"
        onConfirm={() => confirmDelete !== null && handleDelete(confirmDelete)}
        onCancel={() => setConfirmDelete(null)}
      />

      <Card>
        <CardHeader>
          <CardTitle>添加课程</CardTitle>
          <CardDescription>添加新的课程信息</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Input
                label="课程代码"
                placeholder="如：CS101"
                value={form.course_code}
                onChange={(e) => setForm({ ...form, course_code: e.target.value })}
                required
              />
              <Input
                label="课程名称"
                placeholder="如：高等数学"
                value={form.course_name}
                onChange={(e) => setForm({ ...form, course_name: e.target.value })}
                required
              />
              <Input
                label="学分"
                type="number"
                min="0"
                step="0.5"
                placeholder="如：3.0"
                value={form.credit}
                onChange={(e) => setForm({ ...form, credit: e.target.value })}
                required
              />
              <Input
                label="学期"
                placeholder="如：2024-2025-1"
                value={form.semester}
                onChange={(e) => setForm({ ...form, semester: e.target.value })}
              />
              <div className="flex items-end">
                <Switch
                  label="是否必修"
                  checked={form.is_compulsory}
                  onChange={(checked) => setForm({ ...form, is_compulsory: checked })}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>添加课程</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>课程列表</CardTitle>
          <CardDescription>所有已添加的课程</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-muted">加载中...</div>
          ) : courses.length === 0 ? (
            <div className="text-center py-8 text-text-muted">暂无课程</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>课程代码</TableHead>
                  <TableHead>课程名称</TableHead>
                  <TableHead>学分</TableHead>
                  <TableHead>学期</TableHead>
                  <TableHead>类型</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {courses.map((course) => (
                  <TableRow key={course.course_id}>
                    <TableCell className="font-mono text-sm">{course.course_code}</TableCell>
                    <TableCell className="font-medium">{course.course_name}</TableCell>
                    <TableCell>{course.credit}</TableCell>
                    <TableCell>{course.semester || '-'}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                        course.is_compulsory
                          ? 'bg-accent-light text-accent-text'
                          : 'bg-info/10 text-info'
                      }`}>
                        {course.is_compulsory ? '必修' : '选修'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setConfirmDelete(course.course_id!)}
                      >
                        删除
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default function DataEntryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">数据录入</h1>
        <p className="text-text-muted mt-1">
          录入学习数据、成绩信息和健康数据，帮助数字孪生更准确地评估你的成长状态
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="study">
            <Tab value="study" label="学习记录">
              <StudyRecordTab />
            </Tab>
            <Tab value="scores" label="成绩录入">
              <ScoreTab />
            </Tab>
            <Tab value="physical" label="身体健康">
              <PhysicalHealthTab />
            </Tab>
            <Tab value="mental" label="心理健康">
              <MentalHealthTab />
            </Tab>
            <Tab value="social" label="社交健康">
              <SocialHealthTab />
            </Tab>
            <Tab value="profile" label="个人信息">
              <ProfileTab />
            </Tab>
            <Tab value="courses" label="课程管理">
              <CourseTab />
            </Tab>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

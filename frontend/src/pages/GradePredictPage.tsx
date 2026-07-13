import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Progress } from '@/components/ui/Progress'
import {
  getCoursesWithScores,
  trainModel,
  predictGrade,
  type CourseWithScores,
  type TrainResult,
  type PredictResult,
} from '@/api/gradePredict'

export default function GradePredictPage() {
  const [courses, setCourses] = useState<CourseWithScores[]>([])
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null)
  const [algorithm, setAlgorithm] = useState<'linear' | 'xgboost'>('linear')
  const [usualScore, setUsualScore] = useState<string>('')
  const [midtermScore, setMidtermScore] = useState<string>('')
  const [trainResult, setTrainResult] = useState<TrainResult | null>(null)
  const [predictResult, setPredictResult] = useState<PredictResult | null>(null)
  const [training, setTraining] = useState(false)
  const [predicting, setPredicting] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

  const handleTrain = async () => {
    setTraining(true)
    setError(null)
    setTrainResult(null)
    setPredictResult(null)

    try {
      const result = await trainModel(selectedCourse, algorithm)
      setTrainResult(result)
      if (result.error) {
        setError(result.error)
      }
    } catch (err) {
      setError('训练失败，请稍后重试')
      console.error('Train failed:', err)
    } finally {
      setTraining(false)
    }
  }

  const handlePredict = async () => {
    const usual = parseFloat(usualScore)
    const midterm = parseFloat(midtermScore)

    if (isNaN(usual) || isNaN(midterm)) {
      setError('请输入有效的成绩')
      return
    }

    if (usual < 0 || usual > 100 || midterm < 0 || midterm > 100) {
      setError('成绩必须在 0-100 之间')
      return
    }

    setPredicting(true)
    setError(null)
    setPredictResult(null)

    try {
      const result = await predictGrade(selectedCourse, usual, midterm)
      setPredictResult(result)
    } catch (err) {
      setError('预测失败，请稍后重试')
      console.error('Predict failed:', err)
    } finally {
      setPredicting(false)
    }
  }

  const getRiskColor = (risk: string) => {
    if (risk.includes('低')) return 'text-success'
    if (risk.includes('中')) return 'text-warning'
    return 'text-danger'
  }

  const getRiskBg = (risk: string) => {
    if (risk.includes('低')) return 'bg-success/10 text-success'
    if (risk.includes('中')) return 'bg-warning/10 text-warning'
    return 'bg-danger/10 text-danger'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">📊</span>
          成绩预测
        </h1>
        <p className="text-text-muted mt-1">基于历史成绩预测期末考试成绩，支持多种算法</p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-danger-light text-danger border border-danger/30">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
          <CardTitle>预测设置</CardTitle>
          <CardDescription>选择课程和算法进行成绩预测</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <Select
              label="选择课程"
              value={selectedCourse ?? ''}
              onChange={(e) => {
                setSelectedCourse(e.target.value ? parseInt(e.target.value) : null)
                setTrainResult(null)
                setPredictResult(null)
              }}
            >
              <option value="">全部课程（综合模型）</option>
              {courses.map(course => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_name}
                </option>
              ))}
            </Select>

            <Select
              label="预测算法"
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value as 'linear' | 'xgboost')}
            >
              <option value="linear">线性回归</option>
              <option value="xgboost">XGBoost</option>
            </Select>

            <Button
              variant="primary"
              onClick={handleTrain}
              isLoading={training}
              className="w-full"
            >
              {training ? '训练中...' : '训练模型'}
            </Button>

            {trainResult && !trainResult.error && (
              <div className="p-4 rounded-lg bg-bg-hover/50 space-y-3">
                <h4 className="text-sm font-semibold text-text-primary">训练结果</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-text-muted">训练样本</span>
                    <p className="text-text-primary font-medium">{trainResult.samples} 条</p>
                  </div>
                  <div>
                    <span className="text-text-muted">算法</span>
                    <p className="text-text-primary font-medium">{trainResult.algorithm}</p>
                  </div>
                  <div>
                    <span className="text-text-muted">交叉验证 MAE</span>
                    <p className="text-text-primary font-medium">{trainResult.cv_mae}</p>
                  </div>
                  <div>
                    <span className="text-text-muted">残差标准差</span>
                    <p className="text-text-primary font-medium">{trainResult.residual_std}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="border-t border-border-default pt-5 space-y-4">
              <h4 className="text-sm font-semibold text-text-primary">输入成绩</h4>
              <Input
                label="平时成绩"
                type="number"
                min={0}
                max={100}
                value={usualScore}
                onChange={(e) => setUsualScore(e.target.value)}
                placeholder="请输入平时成绩 (0-100)"
              />
              <Input
                label="期中成绩"
                type="number"
                min={0}
                max={100}
                value={midtermScore}
                onChange={(e) => setMidtermScore(e.target.value)}
                placeholder="请输入期中成绩 (0-100)"
              />
              <Button
                variant="success"
                onClick={handlePredict}
                isLoading={predicting}
                className="w-full"
                disabled={!usualScore || !midtermScore}
              >
                {predicting ? '预测中...' : '预测成绩'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
          <CardTitle>预测结果</CardTitle>
          <CardDescription>期末成绩预测及置信区间</CardDescription>
          </CardHeader>
          <CardContent>
            {predictResult ? (
              <div className="space-y-6">
                <div className="text-center py-4">
                  <p className="text-sm text-text-muted mb-2">预测期末成绩</p>
                  <p className={`text-6xl font-bold ${getRiskColor(predictResult.risk_level)}`}>
                    {predictResult.predicted_score.toFixed(1)}
                  </p>
                  <p className="text-text-muted mt-1">
                    置信区间: {predictResult.confidence_interval_low.toFixed(1)} ~ {predictResult.confidence_interval_high.toFixed(1)}
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-text-muted">及格概率</span>
                      <span className="font-medium text-text-primary">
                        {predictResult.pass_probability.toFixed(1)}%
                      </span>
                    </div>
                    <Progress
                      value={predictResult.pass_probability}
                      variant={predictResult.pass_probability >= 80 ? 'success' : predictResult.pass_probability >= 50 ? 'warning' : 'danger'}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-lg bg-bg-hover/50">
                    <span className="text-text-muted">风险等级</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBg(predictResult.risk_level)}`}>
                      {predictResult.risk_level}
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-accent-light/50 border border-accent-primary/20">
                  <p className="text-sm text-text-secondary">
                    {predictResult.pass_probability >= 80 && '🎉 恭喜！通过概率很高，继续保持！'}
                    {predictResult.pass_probability >= 50 && predictResult.pass_probability < 80 && '⚠️ 通过概率中等，需要加强复习，重点关注薄弱知识点。'}
                    {predictResult.pass_probability < 50 && '🚨 风险较高，建议立即制定复习计划，寻求老师或同学帮助。'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-text-muted">
                <span className="text-5xl mb-4">📈</span>
                <p>输入成绩后点击预测</p>
                <p className="text-sm mt-1">查看预测结果</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>课程成绩列表</CardTitle>
          <CardDescription>已有成绩数据的课程</CardDescription>
        </CardHeader>
        <CardContent>
          {courses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                <tr className="border-b border-border-default">
                  <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">课程名称</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">平时成绩</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">期中成绩</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">期末成绩</th>
                </tr>
                </thead>
                <tbody>
                  {courses.map(course => (
                    <tr
                      key={course.course_id}
                      className="border-b border-border-default/50 hover:bg-bg-hover/30 transition-colors cursor-pointer"
                      onClick={() => {
                        setSelectedCourse(course.course_id)
                        if (course.usual_score !== undefined) setUsualScore(String(course.usual_score))
                        if (course.midterm_score !== undefined) setMidtermScore(String(course.midterm_score))
                        setTrainResult(null)
                        setPredictResult(null)
                      }}
                    >
                      <td className="py-3 px-4 text-sm text-text-primary">{course.course_name}</td>
                      <td className="py-3 px-4 text-sm text-text-secondary">
                        {course.usual_score !== undefined && course.usual_score !== null ? course.usual_score.toFixed(1) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-text-secondary">
                        {course.midterm_score !== undefined && course.midterm_score !== null ? course.midterm_score.toFixed(1) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-text-secondary">
                        {course.final_score !== undefined && course.final_score !== null ? course.final_score.toFixed(1) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted">
              暂无课程数据
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

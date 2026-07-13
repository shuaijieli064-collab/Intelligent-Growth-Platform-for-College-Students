import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { getCoursesWithScores, type CourseWithScores } from '@/api/gradePredict'
import { getResources, completeResource, type ResourceItem } from '@/api/resource'

const resourceTypeMap: Record<string, { label: string; icon: string; color: string }> = {
  video: { label: '视频', icon: '🎬', color: 'bg-red-500/10 text-red-500' },
  exercise: { label: '练习', icon: '✏️', color: 'bg-blue-500/10 text-blue-500' },
  article: { label: '文章', icon: '📄', color: 'bg-green-500/10 text-green-500' },
  course: { label: '课程', icon: '🎓', color: 'bg-purple-500/10 text-purple-500' },
}

export default function ResourcePage() {
  const [courses, setCourses] = useState<CourseWithScores[]>([])
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null)
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [loading, setLoading] = useState(false)
  const [completingId, setCompletingId] = useState<number | null>(null)

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
    if (!selectedCourse) return

    const fetchResources = async () => {
      setLoading(true)
      try {
        const result = await getResources(selectedCourse)
        setResources(result)
      } catch (err) {
        console.error('Failed to fetch resources:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchResources()
  }, [selectedCourse])

  const handleComplete = async (resourceId: number) => {
    setCompletingId(resourceId)
    try {
      await completeResource(resourceId)
      setResources(prev => prev.map(r =>
        r.id === resourceId ? { ...r, is_completed: true } : r
      ))
    } catch (err) {
      console.error('Failed to complete resource:', err)
    } finally {
      setCompletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">📚</span>
          资源推荐
        </h1>
        <p className="text-text-muted mt-1">基于薄弱知识点的个性化学习资源推荐</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="w-64">
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
        </div>
        <div className="flex items-center gap-4 text-sm pt-5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-text-muted">视频</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-text-muted">练习</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-text-muted">文章</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-text-muted">课程</span>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>推荐资源</CardTitle>
          <CardDescription>为你精选的学习资源，点击查看详情</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="h-40 bg-bg-active rounded-xl animate-pulse" />
              ))}
            </div>
          ) : resources.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resources.map(resource => {
                const typeInfo = resourceTypeMap[resource.resource_type] || {
                  label: resource.resource_type,
                  icon: '📌',
                  color: 'bg-bg-hover text-text-secondary',
                }

                return (
                  <div
                    key={resource.id}
                    className={`p-5 rounded-xl border transition-all duration-200 ${
                      resource.is_completed
                        ? 'bg-success/5 border-success/30 opacity-70'
                        : 'bg-bg-card border-border-default hover:border-accent-primary hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${typeInfo.color}`}>
                        {typeInfo.icon} {typeInfo.label}
                      </span>
                      {resource.is_completed && (
                        <Badge variant="success" size="sm">已完成</Badge>
                      )}
                    </div>

                    <h4 className={`font-semibold mb-2 line-clamp-2 ${
                      resource.is_completed ? 'text-text-muted line-through' : 'text-text-primary'
                    }`}>
                      {resource.title}
                    </h4>

                    {resource.kp_name && (
                      <p className="text-xs text-text-muted mb-2">
                        知识点: {resource.kp_name}
                      </p>
                    )}

                    <p className="text-sm text-text-secondary mb-4 line-clamp-2">
                      {resource.reason}
                    </p>

                    <div className="flex gap-2">
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1"
                      >
                        <Button variant="secondary" size="sm" className="w-full">
                          打开链接
                        </Button>
                      </a>
                      {!resource.is_completed && (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => handleComplete(resource.id!)}
                          isLoading={completingId === resource.id}
                        >
                          完成
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-16 text-text-muted">
              <span className="text-5xl mb-4 block">🎯</span>
              <p className="font-medium text-text-secondary">暂无推荐资源</p>
              <p className="text-sm mt-1">选择课程查看为你推荐的学习资源</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

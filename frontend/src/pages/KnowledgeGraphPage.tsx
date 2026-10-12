import { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { escapeHtml } from '@/utils/safe'
import { useTheme } from '@/hooks/useTheme'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Progress } from '@/components/ui/Progress'
import { getCoursesWithScores, type CourseWithScores } from '@/api/gradePredict'
import {
  getKnowledgeGraph,
  getWeakNodes,
  type KnowledgeGraphData,
  type WeakNode,
  type LearningPathNode,
  getLearningPath,
  createKnowledgePoint,
  deleteKnowledgePoint,
  setPrerequisite,
  removePrerequisite,
} from '@/api/knowledgeGraph'

function Toast({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000)
    return () => clearTimeout(timer)
  }, [onClose])

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
  confirmText = '确认',
  variant = 'danger',
}: {
  open: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  variant?: 'danger' | 'primary'
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
          <Button variant={variant} onClick={onConfirm}>{confirmText}</Button>
        </div>
      </div>
    </div>
  )
}

export default function KnowledgeGraphPage() {
  const { isDark } = useTheme()
  const [courses, setCourses] = useState<CourseWithScores[]>([])
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null)
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null)
  const [weakNodes, setWeakNodes] = useState<WeakNode[]>([])
  const [learningPath, setLearningPath] = useState<LearningPathNode[]>([])
  const [selectedNode, setSelectedNode] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [weakLoading, setWeakLoading] = useState(false)
  const [pathLoading, setPathLoading] = useState(false)

  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const [showAddForm, setShowAddForm] = useState(false)
  const [addForm, setAddForm] = useState({
    kp_name: '',
    difficulty: '1',
    weight: '1.0',
    prerequisite_kp_id: '',
  })
  const [addLoading, setAddLoading] = useState(false)

  const [showSetPrerequisite, setShowSetPrerequisite] = useState(false)
  const [newPrerequisiteId, setNewPrerequisiteId] = useState('')
  const [prerequisiteLoading, setPrerequisiteLoading] = useState(false)

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

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

    const fetchGraph = async () => {
      setLoading(true)
      try {
        const result = await getKnowledgeGraph(selectedCourse)
        setGraphData(result)
      } catch (err) {
        console.error('Failed to fetch knowledge graph:', err)
      } finally {
        setLoading(false)
      }
    }

    const fetchWeakNodes = async () => {
      setWeakLoading(true)
      try {
        const result = await getWeakNodes(selectedCourse)
        setWeakNodes(result)
      } catch (err) {
        console.error('Failed to fetch weak nodes:', err)
      } finally {
        setWeakLoading(false)
      }
    }

    fetchGraph()
    fetchWeakNodes()
    setSelectedNode(null)
    setLearningPath([])
  }, [selectedCourse])

  const refreshData = async () => {
    if (!selectedCourse) return

    const fetchGraph = async () => {
      try {
        const result = await getKnowledgeGraph(selectedCourse)
        setGraphData(result)
      } catch (err) {
        console.error('Failed to fetch knowledge graph:', err)
      }
    }

    const fetchWeakNodes = async () => {
      try {
        const result = await getWeakNodes(selectedCourse)
        setWeakNodes(result)
      } catch (err) {
        console.error('Failed to fetch weak nodes:', err)
      }
    }

    await Promise.all([fetchGraph(), fetchWeakNodes()])
  }

  const handleNodeClick = async (kpId: number) => {
    if (!selectedCourse) return

    setSelectedNode(kpId)
    setShowSetPrerequisite(false)
    setPathLoading(true)
    try {
      const result = await getLearningPath(selectedCourse, kpId)
      setLearningPath(result)
    } catch (err) {
      console.error('Failed to fetch learning path:', err)
    } finally {
      setPathLoading(false)
    }
  }

  const handleAddKnowledgePoint = async () => {
    if (!selectedCourse || !addForm.kp_name.trim()) return

    setAddLoading(true)
    try {
      await createKnowledgePoint(selectedCourse, {
        kp_name: addForm.kp_name.trim(),
        difficulty: parseInt(addForm.difficulty) || 1,
        weight: parseFloat(addForm.weight) || 1.0,
        prerequisite_kp_id: addForm.prerequisite_kp_id ? parseInt(addForm.prerequisite_kp_id) : undefined,
      })
      setToast({ message: '知识点添加成功', type: 'success' })
      setShowAddForm(false)
      setAddForm({ kp_name: '', difficulty: '1', weight: '1.0', prerequisite_kp_id: '' })
      await refreshData()
    } catch (err) {
      console.error('Failed to create knowledge point:', err)
      setToast({ message: '添加失败，请稍后重试', type: 'error' })
    } finally {
      setAddLoading(false)
    }
  }

  const handleDeleteKnowledgePoint = async () => {
    if (!selectedNode) return

    setDeleteLoading(true)
    try {
      await deleteKnowledgePoint(selectedNode)
      setToast({ message: '知识点删除成功', type: 'success' })
      setShowDeleteConfirm(false)
      setSelectedNode(null)
      setLearningPath([])
      await refreshData()
    } catch (err) {
      console.error('Failed to delete knowledge point:', err)
      setToast({ message: (err as { message?: string })?.message || '删除失败，请稍后重试', type: 'error' })
    } finally {
      setDeleteLoading(false)
    }
  }

  const handleSetPrerequisite = async () => {
    if (!selectedNode || !newPrerequisiteId) return

    setPrerequisiteLoading(true)
    try {
      await setPrerequisite(selectedNode, parseInt(newPrerequisiteId))
      setToast({ message: '先修关系设置成功', type: 'success' })
      setShowSetPrerequisite(false)
      setNewPrerequisiteId('')
      await refreshData()
      if (selectedCourse) {
        const result = await getLearningPath(selectedCourse, selectedNode)
        setLearningPath(result)
      }
    } catch (err) {
      console.error('Failed to set prerequisite:', err)
      setToast({ message: '设置失败，请稍后重试', type: 'error' })
    } finally {
      setPrerequisiteLoading(false)
    }
  }

  const handleRemovePrerequisite = async () => {
    if (!selectedNode) return

    setPrerequisiteLoading(true)
    try {
      await removePrerequisite(selectedNode)
      setToast({ message: '先修关系已移除', type: 'success' })
      await refreshData()
      if (selectedCourse) {
        const result = await getLearningPath(selectedCourse, selectedNode)
        setLearningPath(result)
      }
    } catch (err) {
      console.error('Failed to remove prerequisite:', err)
      setToast({ message: (err as { message?: string })?.message || '移除失败，请稍后重试', type: 'error' })
    } finally {
      setPrerequisiteLoading(false)
    }
  }

  const getMasteryColor = (status: string) => {
    switch (status) {
      case 'mastered':
        return '#10b981'
      case 'in_progress':
        return '#f59e0b'
      default:
        return '#ef4444'
    }
  }

  const buildTreeData = () => {
    if (!graphData || graphData.nodes.length === 0) return []

    const nodeMap = new Map(graphData.nodes.map(n => [n.kp_id, n]))
    const childrenMap = new Map<number, number[]>()
    const hasParent = new Set<number>()
    for (const e of graphData.edges) {
      if (!nodeMap.has(e.source) || !nodeMap.has(e.target)) continue
      if (!childrenMap.has(e.source)) childrenMap.set(e.source, [])
      childrenMap.get(e.source)!.push(e.target)
      hasParent.add(e.target)
    }

    const structureColor = isDark ? '#8b93a7' : '#64748b'
    const courseColor = isDark ? '#fbbf24' : '#d97706'

    const toTree = (id: number): Record<string, unknown> => {
      const n = nodeMap.get(id)
      const nt = n?.node_type || 'kp'
      const kids = (childrenMap.get(id) || []).filter(c => nodeMap.has(c)).map(toTree)

      let color: string
      let size: number
      if (nt === 'course') {
        color = courseColor
        size = 64
      } else if (nt === 'chapter') {
        color = structureColor
        size = 46
      } else {
        color = getMasteryColor(n?.mastery_status || 'weak')
        size = Math.max(22, Math.min(40, (n?.mastery_level || 0) / 2 + 16))
      }

      return {
        name: n?.kp_name || `KP-${id}`,
        kp_id: id,
        node_type: nt,
        symbolSize: size,
        itemStyle: {
          color,
          borderColor: isDark ? '#212226' : '#ffffff',
          borderWidth: nt === 'kp' ? 2 : 3,
          shadowBlur: nt === 'kp' ? 8 : 14,
          shadowColor: color + '40',
        },
        children: kids.length ? kids : undefined,
      }
    }

    return graphData.nodes
      .filter(n => !hasParent.has(n.kp_id))
      .map(n => toTree(n.kp_id))
  }

  const graphOption = graphData ? {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const node = graphData.nodes.find(n => n.kp_id === params.data.kp_id)
          const typeLabel = params.data.node_type === 'course' ? '课程'
            : params.data.node_type === 'chapter' ? '章节' : '知识点'
          return `<div style="font-weight: 600;">${escapeHtml(params.name)}</div>
                  <div>类型: ${typeLabel}</div>
                  ${params.data.node_type === 'kp' ? `<div>掌握度: ${Number(node?.mastery_level || 0).toFixed(1)}%</div>` : ''}`
        }
        return ''
      },
    },
    series: [
      {
        type: 'tree',
        data: buildTreeData(),
        layout: 'orthogonal',
        orient: 'LR',
        roam: true,
        initialTreeDepth: 3,
        zoom: 0.82,
        center: ['48%', '50%'],
        symbol: 'circle',
        label: {
          position: 'left',
          fontSize: 11,
          color: isDark ? '#c9c9cf' : '#374151',
          backgroundColor: 'transparent',
          padding: [2, 4],
        },
        leaves: {
          label: {
            position: 'right',
          },
        },
        lineStyle: {
          color: isDark ? '#3a3d45' : '#d4d2ce',
          width: 1.5,
          curveness: 0.4,
        },
        itemStyle: {
          borderWidth: 2,
        },
        emphasis: {
          focus: 'ancestor',
        },
        expandAndCollapse: true,
        animationDuration: 400,
        animationDurationUpdate: 600,
      },
    ],
  } : {}

  const selectedNodeData = selectedNode ? graphData?.nodes.find(n => n.kp_id === selectedNode) : null

  const getPrerequisiteNode = () => {
    if (!selectedNode || !graphData) return null
    const edge = graphData.edges.find(e => e.target === selectedNode)
    if (!edge) return null
    return graphData.nodes.find(n => n.kp_id === edge.source) || null
  }

  const prerequisiteNode = getPrerequisiteNode()

  const availableNodesForPrerequisite = graphData?.nodes.filter(n => n.kp_id !== selectedNode) || []

  return (
    <div className="space-y-6 relative">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <ConfirmDialog
        open={showDeleteConfirm}
        title="确认删除"
        message={`确定要删除知识点「${selectedNodeData?.kp_name}」吗？此操作不可撤销。`}
        onConfirm={handleDeleteKnowledgePoint}
        onCancel={() => setShowDeleteConfirm(false)}
        confirmText={deleteLoading ? '删除中...' : '确认删除'}
        variant="danger"
      />

      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
          <span className="text-3xl">🕸️</span>
          知识图谱
        </h1>
        <p className="text-text-muted mt-1">可视化课程知识结构，掌握薄弱知识点</p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
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
        <div className="pt-6">
          <Button
            variant="primary"
            onClick={() => setShowAddForm(!showAddForm)}
            leftIcon={<span className="text-lg">+</span>}
          >
            添加知识点
          </Button>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-success" />
            <span className="text-text-muted">已掌握 (≥80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-warning" />
            <span className="text-text-muted">学习中 (50-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-danger" />
            <span className="text-text-muted">薄弱 (&lt;50%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            <span className="text-text-muted">课程/章节</span>
          </div>
        </div>
      </div>

      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>添加知识点</CardTitle>
            <CardDescription>为当前课程添加新的知识点</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="知识点名称"
                placeholder="请输入知识点名称"
                value={addForm.kp_name}
                onChange={(e) => setAddForm({ ...addForm, kp_name: e.target.value })}
              />
              <Input
                label="难度 (1-5)"
                type="number"
                min={1}
                max={5}
                placeholder="1"
                value={addForm.difficulty}
                onChange={(e) => setAddForm({ ...addForm, difficulty: e.target.value })}
              />
              <Input
                label="权重"
                type="number"
                step="0.1"
                placeholder="1.0"
                value={addForm.weight}
                onChange={(e) => setAddForm({ ...addForm, weight: e.target.value })}
              />
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1.5">先修知识点（可选）</label>
                <select
                  className="w-full px-4 py-2.5 pr-10 rounded-lg bg-bg-input text-text-primary border border-border-default transition-all duration-200 ease-out focus:outline-none focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20 appearance-none cursor-pointer"
                  value={addForm.prerequisite_kp_id}
                  onChange={(e) => setAddForm({ ...addForm, prerequisite_kp_id: e.target.value })}
                >
                  <option value="">无</option>
                  {graphData?.nodes.map(node => (
                    <option key={node.kp_id} value={node.kp_id}>
                      {node.kp_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-5">
              <Button variant="secondary" onClick={() => setShowAddForm(false)}>
                取消
              </Button>
              <Button
                variant="primary"
                onClick={handleAddKnowledgePoint}
                isLoading={addLoading}
                disabled={!addForm.kp_name.trim()}
              >
                确认添加
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>知识图谱</CardTitle>
            <CardDescription>点击节点查看详情</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[500px]">
              {loading ? (
                <div className="h-full flex items-center justify-center text-text-muted">
                  加载中...
                </div>
              ) : graphData && graphData.nodes.length > 0 ? (
                <ReactECharts
                  option={graphOption}
                  style={{ height: '100%', width: '100%' }}
                  onEvents={{
                    click: (params: any) => {
                      if (params.dataType === 'node' && params.data?.kp_id) {
                        handleNodeClick(params.data.kp_id)
                      }
                    },
                  }}
                />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-text-muted">
                  <span className="text-5xl mb-4">📚</span>
                  <p>暂无知识图谱数据</p>
                  <p className="text-sm mt-1">点击上方"添加知识点"开始构建</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>薄弱知识点</CardTitle>
              <CardDescription>需要重点学习的内容</CardDescription>
            </CardHeader>
            <CardContent>
              {weakLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-12 bg-bg-active rounded animate-pulse" />
                  ))}
                </div>
              ) : weakNodes.length > 0 ? (
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {weakNodes.map(node => (
                    <div
                      key={node.kp_id}
                      className="p-3 rounded-lg bg-bg-hover/50 hover:bg-bg-hover transition-colors cursor-pointer"
                      onClick={() => handleNodeClick(node.kp_id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-text-primary">{node.kp_name}</span>
                        <span className="text-xs text-danger font-medium">{node.mastery.toFixed(0)}%</span>
                      </div>
                      <Progress value={node.mastery} variant="danger" size="sm" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-text-muted">
                  <p>🎉 太棒了！</p>
                  <p className="text-sm mt-1">没有薄弱知识点</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>节点详情</CardTitle>
              <CardDescription>
                {selectedNodeData ? selectedNodeData.kp_name : '点击节点查看详情'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedNodeData ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-text-muted mb-1">掌握度</p>
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <Progress
                          value={selectedNodeData.mastery_level}
                          variant={
                            selectedNodeData.mastery_status === 'mastered' ? 'success' :
                            selectedNodeData.mastery_status === 'in_progress' ? 'warning' : 'danger'
                          }
                        />
                      </div>
                      <span className="text-sm font-semibold text-text-primary">
                        {selectedNodeData.mastery_level.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-text-muted mb-1">先修知识点</p>
                    <p className="text-sm font-medium text-text-primary">
                      {prerequisiteNode ? prerequisiteNode.kp_name : '无'}
                    </p>
                  </div>

                  {selectedNodeData.is_owner === false && (
                    <div className="p-3 bg-bg-hover/50 rounded-lg text-center">
                      <p className="text-sm font-medium text-text-primary">预置知识点</p>
                      <p className="text-xs text-text-muted mt-1">系统共享内容，只读；可添加自己的知识点并关联到它</p>
                    </div>
                  )}

                  {selectedNodeData.is_owner !== false && (showSetPrerequisite ? (
                    <div className="space-y-3 p-3 bg-bg-hover/50 rounded-lg">
                      <div>
                        <label className="block text-sm font-medium text-text-primary mb-1.5">选择先修知识点</label>
                        <select
                          className="w-full px-4 py-2.5 pr-10 rounded-lg bg-bg-input text-text-primary border border-border-default transition-all duration-200 ease-out focus:outline-none focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20 appearance-none cursor-pointer"
                          value={newPrerequisiteId}
                          onChange={(e) => setNewPrerequisiteId(e.target.value)}
                        >
                          <option value="">请选择...</option>
                          {availableNodesForPrerequisite.map(node => (
                            <option key={node.kp_id} value={node.kp_id}>
                              {node.kp_name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={handleSetPrerequisite}
                          isLoading={prerequisiteLoading}
                          disabled={!newPrerequisiteId}
                        >
                          确认设置
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            setShowSetPrerequisite(false)
                            setNewPrerequisiteId('')
                          }}
                        >
                          取消
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="w-full"
                        onClick={() => setShowSetPrerequisite(true)}
                        isLoading={prerequisiteLoading}
                      >
                        {prerequisiteNode ? '修改先修关系' : '设置先修关系'}
                      </Button>
                      {prerequisiteNode && (
                        <Button
                          variant="secondary"
                          size="sm"
                          className="w-full"
                          onClick={handleRemovePrerequisite}
                          isLoading={prerequisiteLoading}
                        >
                          移除先修关系
                        </Button>
                      )}
                    </div>
                  ))}

                  {selectedNodeData.is_owner !== false && (
                    <div className="pt-3 border-t border-border-default">
                      <Button
                        variant="danger"
                        size="sm"
                        className="w-full"
                        onClick={() => setShowDeleteConfirm(true)}
                      >
                        删除知识点
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-6 text-text-muted">
                  <p>点击左侧图谱节点</p>
                  <p className="text-sm mt-1">查看节点详情</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>学习路径</CardTitle>
              <CardDescription>
                {selectedNodeData ? `到达「${selectedNodeData.kp_name}」的路径` : '点击节点查看路径'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pathLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-10 bg-bg-active rounded animate-pulse" />
                  ))}
                </div>
              ) : learningPath.length > 0 ? (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {learningPath.map((node, index) => (
                    <div key={node.kp_id} className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                        node.mastery >= 80 ? 'bg-success/20 text-success' :
                        node.mastery >= 50 ? 'bg-warning/20 text-warning' :
                        'bg-danger/20 text-danger'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-text-primary">{node.kp_name}</p>
                        <p className="text-xs text-text-muted">掌握度: {node.mastery.toFixed(0)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-text-muted">
                  <p>点击左侧图谱节点</p>
                  <p className="text-sm mt-1">查看学习路径</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

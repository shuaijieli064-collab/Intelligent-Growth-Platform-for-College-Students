import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface KnowledgeNode {
  kp_id: number
  kp_name: string
  mastery_level: number
  mastery_status: string
  /** true = 当前学生自建（可编辑）；false/缺省 = 系统预置（只读） */
  is_owner?: boolean
  /** 节点类型：course=课程根 / chapter=章 / kp=知识点叶子 */
  node_type?: string
}

export interface KnowledgeEdge {
  source: number
  target: number
}

export interface KnowledgeGraphData {
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
}

export interface WeakNode {
  kp_id: number
  kp_name: string
  mastery: number
}

export interface LearningPathNode {
  kp_id: number
  kp_name: string
  mastery: number
  order: number
}

export const getKnowledgeGraph = async (
  courseId: number
): Promise<KnowledgeGraphData> => {
  const response = await apiClient.get<ApiResponse<KnowledgeGraphData>>(
    `/api/knowledge-graph/${courseId}`
  )
  return (response as unknown as ApiResponse<KnowledgeGraphData>).data!
}

export const getWeakNodes = async (
  courseId: number
): Promise<WeakNode[]> => {
  const response = await apiClient.get<ApiResponse<WeakNode[]>>(
    `/api/knowledge-graph/${courseId}/weak-nodes`
  )
  return (response as unknown as ApiResponse<WeakNode[]>).data || []
}

export const getLearningPath = async (
  courseId: number,
  kpId: number
): Promise<LearningPathNode[]> => {
  const response = await apiClient.get<ApiResponse<LearningPathNode[]>>(
    `/api/knowledge-graph/${courseId}/learning-path/${kpId}`
  )
  return (response as unknown as ApiResponse<LearningPathNode[]>).data || []
}

export interface KnowledgePointInfo {
  kp_id: number
  kp_name: string
  course_id: number
  parent_kp_id: number | null
  difficulty: number
  weight: number
}

export const createKnowledgePoint = async (
  courseId: number,
  data: { kp_name: string; difficulty?: number; weight?: number; prerequisite_kp_id?: number }
): Promise<KnowledgePointInfo> => {
  const response = await apiClient.post<ApiResponse<KnowledgePointInfo>>(
    `/api/knowledge-graph/${courseId}/nodes`,
    data
  )
  return (response as unknown as ApiResponse<KnowledgePointInfo>).data!
}

export const deleteKnowledgePoint = async (kpId: number): Promise<void> => {
  await apiClient.delete(`/api/knowledge-graph/nodes/${kpId}`)
}

export const setPrerequisite = async (kpId: number, prerequisiteKpId: number): Promise<void> => {
  await apiClient.put(`/api/knowledge-graph/nodes/${kpId}/prerequisite`, {
    prerequisite_kp_id: prerequisiteKpId,
  })
}

export const removePrerequisite = async (kpId: number): Promise<void> => {
  await apiClient.delete(`/api/knowledge-graph/nodes/${kpId}/prerequisite`)
}

import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface ResourceItem {
  id?: number
  student_id?: number
  kp_id?: number
  kp_name?: string
  resource_type: string
  title: string
  url: string
  reason: string
  is_completed: boolean
  created_at?: string
}

export const getResources = async (
  courseId: number
): Promise<ResourceItem[]> => {
  const response = await apiClient.get<ApiResponse<ResourceItem[]>>(
    `/api/resource/${courseId}`
  )
  return (response as unknown as ApiResponse<ResourceItem[]>).data || []
}

export const completeResource = async (resourceId: number): Promise<void> => {
  await apiClient.put(`/api/resource/${resourceId}/complete`)
}

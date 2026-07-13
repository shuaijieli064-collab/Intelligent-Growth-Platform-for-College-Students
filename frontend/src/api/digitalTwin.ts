import apiClient from '@/api'
import type { ApiResponse, PaginatedResponse } from '@/types'

export interface HealthDimensions {
  academic: number
  physical: number
  mental: number
  social: number
}

export interface DigitalTwinData {
  overall_health: number
  risk_level: string
  dimensions: HealthDimensions
  assessment_date?: string
}

export interface HealthAssessmentItem {
  assessment_id?: number
  assessment_date?: string
  academic_score: number
  physical_score: number
  mental_score: number
  social_score: number
  overall_health: number
  risk_level: string
}

export const getDigitalTwin = async (): Promise<DigitalTwinData> => {
  const response = await apiClient.get<ApiResponse<DigitalTwinData>>(`/api/digital-twin/me`)
  return (response as unknown as ApiResponse<DigitalTwinData>).data!
}

export const getDigitalTwinHistory = async (
  page: number = 1,
  pageSize: number = 20
): Promise<{ items: HealthAssessmentItem[]; total: number; page: number; page_size: number }> => {
  const response = await apiClient.get<PaginatedResponse<HealthAssessmentItem>>(
    `/api/digital-twin/me/history`,
    { params: { page, page_size: pageSize } }
  )
  const data = (response as unknown as PaginatedResponse<HealthAssessmentItem>).data!
  return data
}

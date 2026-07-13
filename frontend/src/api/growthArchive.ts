import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface GrowthReportListItem {
  id: number
  student_id?: number
  report_type: string
  period_start: string
  period_end: string
  title: string
  created_at: string
}

export interface GrowthReportDetail {
  id: number
  report_type: string
  title: string
  period_start: string
  period_end: string
  academic_score: number
  physical_score: number
  mental_score: number
  social_score: number
  overall_score: number
  total_study_hours: number
  task_completion_rate: number
  avg_focus_score: number
  active_days: number
  highlights: string[]
  suggestions: string[]
  created_at: string
}

export const getReports = async (): Promise<GrowthReportListItem[]> => {
  const response = await apiClient.get<ApiResponse<GrowthReportListItem[]>>(
    `/api/growth-archive/reports`
  )
  return (response as unknown as ApiResponse<GrowthReportListItem[]>).data || []
}

export const generateReport = async (
  reportType: string
): Promise<GrowthReportDetail> => {
  const response = await apiClient.post<ApiResponse<GrowthReportDetail>>(
    `/api/growth-archive/generate`,
    { report_type: reportType }
  )
  return (response as unknown as ApiResponse<GrowthReportDetail>).data!
}

export const getReportDetail = async (
  reportId: number
): Promise<GrowthReportDetail> => {
  const response = await apiClient.get<ApiResponse<GrowthReportDetail>>(
    `/api/growth-archive/${reportId}`
  )
  return (response as unknown as ApiResponse<GrowthReportDetail>).data!
}

import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface RiskAlert {
  alert_id?: number
  student_id?: number
  alert_type: string
  risk_level: string
  alert_message: string
  rule_triggered: string
  is_resolved: boolean
  created_at?: string
  resolved_at?: string
}

export type AlertFilter = 'all' | 'unresolved' | 'resolved'

export const getAlerts = async (
  filter: AlertFilter = 'all'
): Promise<RiskAlert[]> => {
  const response = await apiClient.get<ApiResponse<RiskAlert[]>>(
    `/api/risk-warning`,
    { params: { filter } }
  )
  return (response as unknown as ApiResponse<RiskAlert[]>).data || []
}

export const resolveAlert = async (alertId: number): Promise<void> => {
  await apiClient.put(`/api/risk-warning/${alertId}/resolve`)
}

export const deleteAlert = async (alertId: number): Promise<void> => {
  await apiClient.delete(`/api/risk-warning/${alertId}`)
}

export const batchDeleteAlerts = async (
  alertIds: number[]
): Promise<{ deleted_count: number }> => {
  const response = await apiClient.delete<ApiResponse<{ deleted_count: number }>>(
    `/api/risk-warning/batch`,
    { data: { alert_ids: alertIds } }
  )
  return (response as unknown as ApiResponse<{ deleted_count: number }>).data!
}

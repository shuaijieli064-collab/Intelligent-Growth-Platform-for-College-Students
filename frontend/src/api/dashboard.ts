import apiClient from '@/api'
import type { DashboardData, ApiResponse } from '@/types'

export const getDashboard = async (): Promise<DashboardData> => {
  const response = await apiClient.get<ApiResponse<DashboardData>>(`/api/dashboard/me`)
  return (response as unknown as ApiResponse<DashboardData>).data!
}

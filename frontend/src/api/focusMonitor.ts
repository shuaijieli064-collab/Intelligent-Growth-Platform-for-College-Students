import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface FocusDailyData {
  date: string
  focus_score: number
  total_minutes: number
}

export interface FocusMonitorData {
  realtime_score: number
  level: string
  trend: string
  last_14_days: FocusDailyData[]
  last_30_days: FocusDailyData[]
}

export const getFocusData = async (): Promise<FocusMonitorData> => {
  const response = await apiClient.get<ApiResponse<FocusMonitorData>>(
    `/api/focus-monitor`
  )
  return (response as unknown as ApiResponse<FocusMonitorData>).data!
}

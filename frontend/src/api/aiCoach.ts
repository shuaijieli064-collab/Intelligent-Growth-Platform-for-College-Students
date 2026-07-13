import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface CoachSession {
  session_id: string
  msg_count: number
  started_at?: string
}

export interface CoachMessage {
  log_id?: number
  session_id: string
  role: string
  message: string
  tokens_used: number
  created_at?: string
}

export type QuickActionType =
  | 'study_advice'
  | 'emotional_support'
  | 'career_planning'
  | 'grade_analysis'
  | 'daily_motivation'

export const getSessions = async (): Promise<CoachSession[]> => {
  const response = await apiClient.get<ApiResponse<CoachSession[]>>(
    `/api/ai-coach/sessions`
  )
  return (response as unknown as ApiResponse<CoachSession[]>).data || []
}

export const getMessages = async (
  sessionId: string
): Promise<CoachMessage[]> => {
  const response = await apiClient.get<ApiResponse<CoachMessage[]>>(
    `/api/ai-coach/messages/${sessionId}`
  )
  return (response as unknown as ApiResponse<CoachMessage[]>).data || []
}

export const sendMessage = async (
  sessionId: string | null,
  message: string
): Promise<CoachMessage> => {
  const response = await apiClient.post<ApiResponse<CoachMessage>>(
    `/api/ai-coach/chat`,
    {
      session_id: sessionId,
      message,
    }
  )
  return (response as unknown as ApiResponse<CoachMessage>).data!
}

export const sendQuickAction = async (
  actionType: QuickActionType
): Promise<CoachMessage> => {
  const response = await apiClient.post<ApiResponse<CoachMessage>>(
    `/api/ai-coach/quick-action`,
    {
      action_type: actionType,
    }
  )
  return (response as unknown as ApiResponse<CoachMessage>).data!
}

export const createNewSession = async (): Promise<{ session_id: string }> => {
  const response = await apiClient.post<ApiResponse<{ session_id: string }>>(
    `/api/ai-coach/new-session`
  )
  return (response as unknown as ApiResponse<{ session_id: string }>).data!
}

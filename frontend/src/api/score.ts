import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface Score {
  id?: number
  student_id?: number
  course_id: number
  course_name: string
  usual_score?: number | null
  midterm_score?: number | null
  final_score?: number | null
  predicted_final?: number | null
  has_final_exam: boolean
}

export interface ScoreCreate {
  course_id: number
  usual_score?: number | null
  midterm_score?: number | null
  final_score?: number | null
  has_final_exam?: boolean
}

export const getScores = async (): Promise<Score[]> => {
  const response = await apiClient.get<ApiResponse<Score[]>>(
    `/api/scores`
  )
  return (response as unknown as ApiResponse<Score[]>).data || []
}

export const createOrUpdateScore = async (
  data: ScoreCreate
): Promise<Score> => {
  const response = await apiClient.post<ApiResponse<Score>>(
    `/api/scores`,
    data
  )
  return (response as unknown as ApiResponse<Score>).data!
}

export const deleteScore = async (scId: number): Promise<void> => {
  await apiClient.delete(`/api/scores/${scId}`)
}

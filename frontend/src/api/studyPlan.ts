import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface StudyPlanTask {
  day: number
  task: string
  type: string
  duration_min: number
  priority: string
  done: boolean
}

export interface StudyPlan {
  id?: number
  student_id?: number
  subject: string
  goal_score: number
  exam_date: string
  plan_content: StudyPlanTask[]
  status: string
  progress: number
  created_at?: string
}

export interface GeneratePlanRequest {
  subject: string
  course_id: number
  goal_score: number
  exam_date: string
  daily_minutes: number
}

export const getStudyPlan = async (): Promise<StudyPlan | null> => {
  const response = await apiClient.get<ApiResponse<StudyPlan | null>>(
    `/api/study-plan`
  )
  return (response as unknown as ApiResponse<StudyPlan | null>).data || null
}

export const generatePlan = async (
  data: GeneratePlanRequest
): Promise<StudyPlan> => {
  const response = await apiClient.post<ApiResponse<StudyPlan>>(
    `/api/study-plan/generate`,
    data
  )
  return (response as unknown as ApiResponse<StudyPlan>).data!
}

export const updateTask = async (
  taskIndex: number,
  done: boolean
): Promise<{ task_index: number; done: boolean; progress: number }> => {
  const response = await apiClient.put<ApiResponse<{ task_index: number; done: boolean; progress: number }>>(
    `/api/study-plan/task/${taskIndex}`,
    { done }
  )
  return (response as unknown as ApiResponse<{ task_index: number; done: boolean; progress: number }>).data!
}

export const completeNextTask = async (
): Promise<{ task_index: number; task: string; progress: number; completed_all: boolean }> => {
  const response = await apiClient.post<ApiResponse<{ task_index: number; task: string; progress: number; completed_all: boolean }>>(
    `/api/study-plan/next-task`
  )
  return (response as unknown as ApiResponse<{ task_index: number; task: string; progress: number; completed_all: boolean }>).data!
}

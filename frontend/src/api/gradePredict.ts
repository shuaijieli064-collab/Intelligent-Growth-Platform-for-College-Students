import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface CourseWithScores {
  course_id: number
  course_name: string
  usual_score?: number
  midterm_score?: number
  final_score?: number
}

export interface TrainResult {
  samples: number
  cv_mae: number
  residual_std: number
  algorithm: string
  error?: string
}

export interface PredictResult {
  predicted_score: number
  confidence_interval_low: number
  confidence_interval_high: number
  pass_probability: number
  risk_level: string
}

export const getCoursesWithScores = async (): Promise<CourseWithScores[]> => {
  const response = await apiClient.get<ApiResponse<CourseWithScores[]>>(
    '/api/grade-predict/courses'
  )
  return (response as unknown as ApiResponse<CourseWithScores[]>).data || []
}

export const trainModel = async (
  courseId: number | null,
  algorithm: 'linear' | 'xgboost'
): Promise<TrainResult> => {
  const response = await apiClient.post<ApiResponse<TrainResult>>(
    '/api/grade-predict/train',
    {
      course_id: courseId,
      algorithm,
    }
  )
  return (response as unknown as ApiResponse<TrainResult>).data!
}

export const predictGrade = async (
  courseId: number | null,
  usualScore: number,
  midtermScore: number
): Promise<PredictResult> => {
  const response = await apiClient.post<ApiResponse<PredictResult>>(
    '/api/grade-predict/predict',
    {
      course_id: courseId,
      usual_score: usualScore,
      midterm_score: midtermScore,
    }
  )
  return (response as unknown as ApiResponse<PredictResult>).data!
}

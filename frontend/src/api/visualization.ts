import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface StudyCurvePoint {
  date: string
  study_minutes: number
  focus_score: number
  avg_7day: number
}

export interface StudyCurveData {
  data: StudyCurvePoint[]
}

export interface HealthTrendPoint {
  date: string
  overall: number
  academic: number
  physical: number
  mental: number
  social: number
}

export interface HealthTrendData {
  data: HealthTrendPoint[]
}

export interface GradeRadarCourse {
  course_name: string
  score: number
}

export interface GradeRadarData {
  courses: GradeRadarCourse[]
  dimensions: string[]
}

export interface KnowledgeHeatmapCell {
  course_name: string
  kp_name: string
  mastery: number
}

export interface KnowledgeHeatmapData {
  courses: string[]
  kps: string[]
  data: KnowledgeHeatmapCell[]
}

export const getStudyCurve = async (): Promise<StudyCurveData> => {
  const response = await apiClient.get<ApiResponse<StudyCurveData>>(
    `/api/visualization/study-curve`
  )
  return (response as unknown as ApiResponse<StudyCurveData>).data!
}

export const getHealthTrend = async (): Promise<HealthTrendData> => {
  const response = await apiClient.get<ApiResponse<HealthTrendData>>(
    `/api/visualization/health-trend`
  )
  return (response as unknown as ApiResponse<HealthTrendData>).data!
}

export const getGradeRadar = async (): Promise<GradeRadarData> => {
  const response = await apiClient.get<ApiResponse<GradeRadarData>>(
    `/api/visualization/grade-radar`
  )
  return (response as unknown as ApiResponse<GradeRadarData>).data!
}

export const getKnowledgeHeatmap = async (): Promise<KnowledgeHeatmapData> => {
  const response = await apiClient.get<ApiResponse<KnowledgeHeatmapData>>(
    `/api/visualization/knowledge-heatmap`
  )
  return (response as unknown as ApiResponse<KnowledgeHeatmapData>).data!
}

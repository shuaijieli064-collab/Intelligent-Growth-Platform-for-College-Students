import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface PhysicalHealthRecord {
  id?: number
  student_id?: number
  record_date?: string | null
  exercise_type?: string | null
  exercise_duration: number
  sleep_hours?: number | null
  steps: number
}

export interface PhysicalHealthCreate {
  record_date: string
  exercise_type?: string | null
  exercise_duration?: number
  sleep_hours?: number | null
  steps?: number
}

export interface MentalHealthRecord {
  id?: number
  student_id?: number
  record_date?: string | null
  mood_score?: number | null
  stress_level?: number | null
  anxiety_level?: number | null
  notes?: string | null
}

export interface MentalHealthCreate {
  record_date: string
  mood_score?: number | null
  stress_level?: number | null
  anxiety_level?: number | null
  notes?: string | null
}

export interface SocialHealthRecord {
  id?: number
  student_id?: number
  record_date?: string | null
  activity_type?: string | null
  duration_minutes: number
  interaction_count: number
}

export interface SocialHealthCreate {
  record_date: string
  activity_type?: string | null
  duration_minutes?: number
  interaction_count?: number
}

export const getPhysicalHealth = async (): Promise<PhysicalHealthRecord[]> => {
  const response = await apiClient.get<ApiResponse<PhysicalHealthRecord[]>>(
    `/api/physical-health`
  )
  return (response as unknown as ApiResponse<PhysicalHealthRecord[]>).data || []
}

export const createPhysicalHealth = async (
  data: PhysicalHealthCreate
): Promise<PhysicalHealthRecord> => {
  const response = await apiClient.post<ApiResponse<PhysicalHealthRecord>>(
    `/api/physical-health`,
    data
  )
  return (response as unknown as ApiResponse<PhysicalHealthRecord>).data!
}

export const deletePhysicalHealth = async (recordId: number): Promise<void> => {
  await apiClient.delete(`/api/physical-health/${recordId}`)
}

export const getMentalHealth = async (): Promise<MentalHealthRecord[]> => {
  const response = await apiClient.get<ApiResponse<MentalHealthRecord[]>>(
    `/api/mental-health`
  )
  return (response as unknown as ApiResponse<MentalHealthRecord[]>).data || []
}

export const createMentalHealth = async (
  data: MentalHealthCreate
): Promise<MentalHealthRecord> => {
  const response = await apiClient.post<ApiResponse<MentalHealthRecord>>(
    `/api/mental-health`,
    data
  )
  return (response as unknown as ApiResponse<MentalHealthRecord>).data!
}

export const deleteMentalHealth = async (recordId: number): Promise<void> => {
  await apiClient.delete(`/api/mental-health/${recordId}`)
}

export const getSocialHealth = async (): Promise<SocialHealthRecord[]> => {
  const response = await apiClient.get<ApiResponse<SocialHealthRecord[]>>(
    `/api/social-health`
  )
  return (response as unknown as ApiResponse<SocialHealthRecord[]>).data || []
}

export const createSocialHealth = async (
  data: SocialHealthCreate
): Promise<SocialHealthRecord> => {
  const response = await apiClient.post<ApiResponse<SocialHealthRecord>>(
    `/api/social-health`,
    data
  )
  return (response as unknown as ApiResponse<SocialHealthRecord>).data!
}

export const deleteSocialHealth = async (recordId: number): Promise<void> => {
  await apiClient.delete(`/api/social-health/${recordId}`)
}

import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface StudyRecord {
  record_id?: number
  student_id?: number
  course_id?: number | null
  study_date?: string | null
  study_hours: number
  task_completed: number
  focus_score?: number | null
  notes?: string | null
  course_name?: string | null
}

export interface StudyRecordCreate {
  study_date: string
  study_hours: number
  course_id?: number | null
  task_completed?: number
  focus_score?: number | null
  notes?: string | null
}

export const getStudyRecords = async (): Promise<StudyRecord[]> => {
  const response = await apiClient.get<ApiResponse<StudyRecord[]>>(
    `/api/study-records`
  )
  return (response as unknown as ApiResponse<StudyRecord[]>).data || []
}

export const createStudyRecord = async (
  data: StudyRecordCreate
): Promise<StudyRecord> => {
  const response = await apiClient.post<ApiResponse<StudyRecord>>(
    `/api/study-records`,
    data
  )
  return (response as unknown as ApiResponse<StudyRecord>).data!
}

export const deleteStudyRecord = async (recordId: number): Promise<void> => {
  await apiClient.delete(`/api/study-records/${recordId}`)
}

export const deleteAllStudyRecords = async (): Promise<void> => {
  await apiClient.delete(`/api/study-records`)
}

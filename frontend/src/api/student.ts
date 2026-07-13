import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface Student {
  student_id?: number
  student_no: string
  name: string
  gender: string
  grade_level: string
  major: string
  enrollment_year: number
  created_at?: string
}

export const getHealth = async (): Promise<{ status: string }> => {
  return await apiClient.get('/api/health')
}

export const getStudents = async (): Promise<Student[]> => {
  const response = await apiClient.get<ApiResponse<Student[]>>('/api/students')
  return (response as unknown as ApiResponse<Student[]>).data || []
}

export const getStudentMe = async (): Promise<Student> => {
  const response = await apiClient.get<ApiResponse<Student>>('/api/students/me')
  return (response as unknown as ApiResponse<Student>).data!
}

export const updateStudentMe = async (data: Partial<Student>): Promise<Student> => {
  const response = await apiClient.put<ApiResponse<Student>>('/api/students/me', data)
  return (response as unknown as ApiResponse<Student>).data!
}

export const getMeInfo = async (): Promise<{ user: Record<string, unknown>; student: Student | null }> => {
  const response = await apiClient.get<ApiResponse<{ user: Record<string, unknown>; student: Student | null }>>('/api/me')
  return (response as unknown as ApiResponse<{ user: Record<string, unknown>; student: Student | null }>).data!
}

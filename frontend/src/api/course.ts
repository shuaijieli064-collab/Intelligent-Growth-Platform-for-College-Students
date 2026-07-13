import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface Course {
  course_id?: number
  course_code: string
  course_name: string
  credit: number
  semester: string
  is_compulsory: boolean
  prerequisite_course_id?: number | null
}

export interface CourseCreate {
  course_code: string
  course_name: string
  credit: number
  semester: string
  is_compulsory: boolean
  prerequisite_course_id?: number | null
}

export const getCourses = async (): Promise<Course[]> => {
  const response = await apiClient.get<ApiResponse<Course[]>>('/api/courses')
  return (response as unknown as ApiResponse<Course[]>).data || []
}

export const getMyCourses = async (): Promise<Course[]> => {
  const response = await apiClient.get<ApiResponse<Course[]>>('/api/courses/my')
  return (response as unknown as ApiResponse<Course[]>).data || []
}

export const createCourse = async (data: CourseCreate): Promise<Course> => {
  const response = await apiClient.post<ApiResponse<Course>>('/api/courses', data)
  return (response as unknown as ApiResponse<Course>).data!
}

export const deleteCourse = async (courseId: number): Promise<void> => {
  await apiClient.delete(`/api/courses/${courseId}`)
}

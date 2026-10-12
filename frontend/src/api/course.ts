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

export const deleteCourse = async (courseId: number): Promise<string> => {
  const response = await apiClient.delete<ApiResponse<{ course_id: number }>>(
    `/api/courses/${courseId}`
  )
  return (response as unknown as ApiResponse<unknown>).message || '课程删除成功'
}

export const restoreDefaultCourses = async (): Promise<string> => {
  const response = await apiClient.post<ApiResponse<{ added: number }>>(
    '/api/courses/restore-defaults'
  )
  return (response as unknown as ApiResponse<unknown>).message || '已恢复默认课程'
}

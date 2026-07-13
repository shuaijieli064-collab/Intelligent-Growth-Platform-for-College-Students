import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface AuthResponse {
  token: string
  user_id: number
  username: string
  email: string
  student_id: number | null
}

export interface UserInfo {
  user_id: number
  username: string
  email: string
  student_id: number | null
  name: string | null
  student_no: string | null
  grade_level: string | null
  major: string | null
}

export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await apiClient.post<ApiResponse<AuthResponse>>('/api/auth/login', { username, password })
  return (response as unknown as ApiResponse<AuthResponse>).data!
}

export const register = async (username: string, password: string, email: string): Promise<AuthResponse> => {
  const response = await apiClient.post<ApiResponse<AuthResponse>>('/api/auth/register', { username, password, email })
  return (response as unknown as ApiResponse<AuthResponse>).data!
}

export const getMe = async (): Promise<UserInfo> => {
  const response = await apiClient.get<ApiResponse<UserInfo>>('/api/auth/me')
  return (response as unknown as ApiResponse<UserInfo>).data!
}

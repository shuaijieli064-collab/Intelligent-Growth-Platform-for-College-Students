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

export interface HealthResponse {
  status: string
}

export interface StudentInfo {
  student_id?: number
  name: string
  student_no: string
  major: string
  grade_level: string
}

export interface HealthDimensions {
  academic: number
  physical: number
  mental: number
  social: number
}

export interface RiskAlertItem {
  alert_id?: number
  alert_type: string
  risk_level: string
  alert_message: string
  created_at?: string
  is_resolved: boolean
}

export interface DashboardData {
  student: StudentInfo
  overall_health: number
  risk_level: string
  active_alert_count: number
  dimensions: HealthDimensions
  recent_alerts: RiskAlertItem[]
}

export interface ApiResponse<T> {
  code: number
  data?: T
  message: string
}

export interface PaginatedResponse<T> {
  code: number
  data?: {
    items: T[]
    total: number
    page: number
    page_size: number
  }
  message: string
}

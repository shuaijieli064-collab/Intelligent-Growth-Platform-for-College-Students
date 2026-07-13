import axios from 'axios'
import type { AxiosError, AxiosResponse } from 'axios'

export interface ApiError {
  code: number
  message: string
  details?: string
}

const apiClient = axios.create({
  baseURL: '',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage)
        const token = parsed?.state?.token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      } catch {
        // ignore parse errors
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
    console.error('API Error:', error)

    let errorMessage = '请求失败，请稍后重试'
    let errorCode = -1

    if (error.response) {
      errorCode = error.response.status
      const data = error.response.data as any

      if (data?.detail) {
        errorMessage = Array.isArray(data.detail)
          ? data.detail.map((d: any) => d.msg || d.message).join(', ')
          : data.detail
      } else if (data?.message) {
        errorMessage = data.message
      } else {
        switch (error.response.status) {
          case 400:
            errorMessage = '请求参数错误'
            break
          case 401:
            errorMessage = '未授权，请重新登录'
            break
          case 403:
            errorMessage = '没有权限访问'
            break
          case 404:
            errorMessage = '请求的资源不存在'
            break
          case 500:
            errorMessage = '服务器内部错误'
            break
          case 502:
            errorMessage = '网关错误'
            break
          case 503:
            errorMessage = '服务不可用'
            break
          case 504:
            errorMessage = '请求超时'
            break
        }
      }

      if (error.response.status === 401) {
        localStorage.removeItem('auth-storage')
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
      }
    } else if (error.request) {
      errorMessage = '网络连接失败，请检查网络设置'
      errorCode = 0
    } else {
      errorMessage = error.message || '请求失败'
    }

    const apiError: ApiError = {
      code: errorCode,
      message: errorMessage,
      details: error.message,
    }

    return Promise.reject(apiError)
  }
)

export default apiClient

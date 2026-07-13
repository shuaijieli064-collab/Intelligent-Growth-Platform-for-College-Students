import apiClient from '@/api'
import type { ApiResponse } from '@/types'

export interface LLMConfig {
  provider: string
  api_url: string
  api_key: string
  model: string
}

export const getLLMConfig = async (): Promise<LLMConfig> => {
  const response = await apiClient.get<ApiResponse<LLMConfig>>('/api/config/llm')
  return (response as unknown as ApiResponse<LLMConfig>).data!
}

export const updateLLMConfig = async (config: LLMConfig): Promise<void> => {
  await apiClient.put<ApiResponse<void>>('/api/config/llm', config)
}

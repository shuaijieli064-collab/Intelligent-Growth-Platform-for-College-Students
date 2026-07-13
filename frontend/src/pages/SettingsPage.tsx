import { useState, useEffect } from 'react'
import { Tabs, Tab } from '@/components/ui/Tabs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { getLLMConfig, updateLLMConfig, type LLMConfig } from '@/api/settings'

const providerDefaults: Record<string, { api_url: string; model: string }> = {
  deepseek: {
    api_url: 'https://api.deepseek.com/v1/chat/completions',
    model: 'deepseek-chat',
  },
  zhipu: {
    api_url: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
    model: 'glm-4',
  },
  qwen: {
    api_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    model: 'qwen-turbo',
  },
  custom: {
    api_url: '',
    model: '',
  },
}

function decodeBase64(s: string): string {
  try {
    return atob(s)
  } catch {
    return s
  }
}

function encodeBase64(s: string): string {
  try {
    return btoa(s)
  } catch {
    return s
  }
}

function AISettingsTab() {
  const [provider, setProvider] = useState('deepseek')
  const [apiUrl, setApiUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  useEffect(() => {
    const fetchConfig = async () => {
      setIsLoading(true)
      try {
        const config = await getLLMConfig()
        setProvider(config.provider || 'deepseek')
        setApiUrl(config.api_url || '')
        setApiKey(decodeBase64(config.api_key || ''))
        setModel(config.model || '')
      } catch (err) {
        console.error('Failed to load LLM config:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchConfig()
  }, [])

  useEffect(() => {
    if (provider !== 'custom') {
      const defaults = providerDefaults[provider]
      if (defaults) {
        setApiUrl(defaults.api_url)
        setModel(defaults.model)
      }
    }
  }, [provider])

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [toast])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const config: LLMConfig = {
        provider,
        api_url: apiUrl,
        api_key: encodeBase64(apiKey),
        model,
      }
      await updateLLMConfig(config)
      setToast({ type: 'success', message: '配置保存成功！' })
    } catch (err) {
      console.error('Failed to save LLM config:', err)
      setToast({ type: 'error', message: '保存失败，请稍后重试' })
    } finally {
      setIsSaving(false)
    }
  }

  const isEditable = provider === 'custom'

  return (
    <div className="relative">
      {toast && (
        <div
          className={`
            fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg
            transition-all duration-300 ease-out animate-slide-in-right
            ${toast.type === 'success' ? 'bg-success text-white' : 'bg-danger text-white'}
          `}
        >
          <div className="flex items-center gap-2">
            <span>{toast.type === 'success' ? '✓' : '✕'}</span>
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        </div>
      )}

      <div className="space-y-5">
        <div>
          <Select
            label="AI 提供商"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isLoading}
          >
            <option value="deepseek">DeepSeek</option>
            <option value="zhipu">智谱AI</option>
            <option value="qwen">通义千问</option>
            <option value="custom">自定义</option>
          </Select>
        </div>

        <div>
          <Input
            label="API Key"
            type={showApiKey ? 'text' : 'password'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="请输入 API Key"
            disabled={isLoading}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="text-text-muted hover:text-text-primary transition-colors pointer-events-auto"
                tabIndex={-1}
              >
                {showApiKey ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            }
          />
        </div>

        <div>
          <Input
            label="API URL"
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            placeholder="请输入 API URL"
            disabled={isLoading || !isEditable}
            className={!isEditable ? 'opacity-70' : ''}
          />
        </div>

        <div>
          <Input
            label="模型名称"
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="请输入模型名称"
            disabled={isLoading || !isEditable}
            className={!isEditable ? 'opacity-70' : ''}
          />
        </div>

        <div className="pt-2">
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={isSaving}
            disabled={isLoading}
          >
            保存配置
          </Button>
        </div>
      </div>
    </div>
  )
}

function AboutTab() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white text-2xl font-bold shadow-md">
          智
        </div>
        <div>
          <h3 className="text-xl font-bold text-text-primary">大学生智能成长平台</h3>
          <p className="text-sm text-text-muted mt-1">Smart Growth Platform for College Students</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 rounded-lg bg-bg-hover/50">
          <div className="text-sm text-text-muted mb-1">版本号</div>
          <div className="text-base font-semibold text-text-primary">v1.0.0</div>
        </div>
        <div className="p-4 rounded-lg bg-bg-hover/50">
          <div className="text-sm text-text-muted mb-1">技术栈</div>
          <div className="text-base font-semibold text-text-primary">FastAPI + React + TypeScript</div>
        </div>
      </div>

      <div className="p-5 rounded-lg bg-bg-hover/30 border border-border-default">
        <div className="text-sm font-semibold text-text-primary mb-2">关于平台</div>
        <p className="text-sm text-text-secondary leading-relaxed">
          大学生智能成长平台是一款面向大学生的综合性成长辅助工具，通过数字孪生、知识图谱、AI 学习教练等先进技术，
          为学生提供全方位的学习规划、成绩预测、风险预警、资源推荐等服务，助力大学生全面成长与发展。
        </p>
      </div>

      <div className="pt-2 text-xs text-text-muted">
        © 2025 大学生智能成长平台. All rights reserved.
      </div>
    </div>
  )
}

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary">设置</h2>
        <p className="text-sm text-text-muted mt-1">管理你的平台配置和偏好</p>
      </div>

      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-lg">系统设置</CardTitle>
          <CardDescription>配置 AI 模型参数和查看平台信息</CardDescription>
        </CardHeader>
        <CardContent className="pt-5">
          <Tabs defaultValue="ai">
            <Tab value="ai" label="AI 配置">
              <AISettingsTab />
            </Tab>
            <Tab value="about" label="关于">
              <AboutTab />
            </Tab>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

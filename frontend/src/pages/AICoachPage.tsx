import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import {
  sendMessage,
  sendQuickAction,
  createNewSession,
  getSessions,
  getMessages,
  type CoachMessage,
  type CoachSession,
  type QuickActionType,
} from '@/api/aiCoach'

const quickActions: { type: QuickActionType; label: string; icon: string }[] = [
  { type: 'study_advice', label: '学习建议', icon: '📚' },
  { type: 'emotional_support', label: '情绪疏导', icon: '💛' },
  { type: 'career_planning', label: '生涯规划', icon: '🎯' },
  { type: 'grade_analysis', label: '成绩分析', icon: '📊' },
  { type: 'daily_motivation', label: '每日激励', icon: '✨' },
]

const GREETING = '你好！我是你的AI学习教练。有什么可以帮助你的吗？你可以问我学习建议、情绪疏导、生涯规划等问题。'

function greetingFor(sessionId: string): CoachMessage {
  return { session_id: sessionId, role: 'assistant', message: GREETING, tokens_used: 0 }
}

export default function AICoachPage() {
  const [messages, setMessages] = useState<CoachMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [quickLoading, setQuickLoading] = useState(false)
  const [sessions, setSessions] = useState<CoachSession[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const refreshSessions = async () => {
    try {
      setSessions(await getSessions())
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  useEffect(() => {
    const initSession = async () => {
      try {
        const result = await createNewSession()
        setSessionId(result.session_id)
        setMessages([greetingFor(result.session_id)])
        refreshSessions()
      } catch (error) {
        console.error('Failed to create session:', error)
        setMessages([greetingFor('')])
      }
    }

    initSession()
  }, [])

  const loadSession = async (sid: string) => {
    if (sid === sessionId || loading || quickLoading) return
    try {
      const msgs = await getMessages(sid)
      setSessionId(sid)
      setMessages(msgs.length ? msgs : [greetingFor(sid)])
    } catch (error) {
      console.error('Failed to load session messages:', error)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return

    const userMessage: CoachMessage = {
      session_id: sessionId || '',
      role: 'user',
      message: inputValue.trim(),
      tokens_used: 0,
    }

    setMessages(prev => [...prev, userMessage])
    const userInput = inputValue.trim()
    setInputValue('')
    setLoading(true)

    try {
      const reply = await sendMessage(sessionId, userInput)
      if (reply.session_id && !sessionId) {
        setSessionId(reply.session_id)
      }
      setMessages(prev => [...prev, reply])
      refreshSessions()
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, {
        session_id: sessionId || '',
        role: 'assistant',
        message: '抱歉，我暂时无法回复，请稍后再试。',
        tokens_used: 0,
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleQuickAction = async (actionType: QuickActionType) => {
    if (quickLoading) return

    setQuickLoading(true)
    try {
      const reply = await sendQuickAction(actionType, sessionId)
      if (reply.session_id) {
        setSessionId(reply.session_id)
      }
      setMessages(prev => [...prev, reply])
      refreshSessions()
    } catch (error) {
      console.error('Quick action failed:', error)
      setMessages(prev => [...prev, {
        session_id: sessionId || '',
        role: 'assistant',
        message: '快捷操作失败，请稍后再试。',
        tokens_used: 0,
      }])
    } finally {
      setQuickLoading(false)
    }
  }

  const handleNewSession = async () => {
    if (loading) return

    try {
      const result = await createNewSession()
      setSessionId(result.session_id)
      setMessages([greetingFor(result.session_id)])
      refreshSessions()
    } catch (error) {
      console.error('Failed to create session:', error)
      setMessages(prev => [...prev, {
        session_id: sessionId || '',
        role: 'assistant',
        message: '新建会话失败，请稍后再试。',
        tokens_used: 0,
      }])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatSessionTime = (s: CoachSession) => {
    if (!s.started_at) return `会话 · ${s.msg_count} 条`
    const d = new Date(s.started_at)
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} · ${s.msg_count} 条`
  }

  return (
    <div className="space-y-6 h-[calc(100vh-120px)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-3">
            <span className="text-3xl">🤖</span>
            AI 学习教练
          </h1>
          <p className="text-text-muted mt-1">你的私人智能学习助手，随时为你答疑解惑</p>
        </div>
        <Button variant="secondary" onClick={handleNewSession} disabled={loading}>
          新对话
        </Button>
      </div>

      <div className="flex gap-6 h-[calc(100%-72px)]">
        <aside className="w-56 shrink-0 hidden md:block">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-text-muted">历史会话</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-2 space-y-1">
              {sessions.length === 0 ? (
                <p className="text-xs text-text-muted px-2 py-3">暂无历史会话</p>
              ) : (
                sessions.map(s => (
                  <button
                    key={s.session_id}
                    type="button"
                    onClick={() => loadSession(s.session_id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${
                      s.session_id === sessionId
                        ? 'bg-accent-primary/10 text-accent-primary font-medium'
                        : 'text-text-secondary hover:bg-bg-hover'
                    }`}
                  >
                    {formatSessionTime(s)}
                  </button>
                ))
              )}
            </CardContent>
          </Card>
        </aside>

        <Card className="flex-1 flex flex-col h-full min-w-0">
        <CardHeader className="pb-4">
          <div className="flex flex-wrap gap-2">
            {quickActions.map(action => (
              <Button
                key={action.type}
                variant="secondary"
                size="sm"
                onClick={() => handleQuickAction(action.type)}
                isLoading={quickLoading}
              >
                <span>{action.icon}</span>
                {action.label}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-text-muted">
                <span className="text-5xl mb-4">👋</span>
                <p>开始和 AI 教练对话吧</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] px-4 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-accent-primary text-white rounded-br-sm'
                        : 'bg-bg-hover text-text-primary rounded-bl-sm'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.message}</p>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-bg-hover px-4 py-3 rounded-2xl rounded-bl-sm">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-border-default">
            <div className="flex gap-3">
              <Input
                placeholder="输入你的问题..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
              />
              <Button
                variant="primary"
                onClick={handleSend}
                isLoading={loading}
                disabled={!inputValue.trim()}
              >
                发送
              </Button>
            </div>
          </div>
        </CardContent>
        </Card>
      </div>
    </div>
  )
}

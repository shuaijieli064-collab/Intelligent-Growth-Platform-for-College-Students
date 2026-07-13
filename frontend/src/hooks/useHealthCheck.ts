import { useEffect, useState } from 'react'
import { getHealth } from '@/api/student'

export const useHealthCheck = () => {
  const [status, setStatus] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const checkHealth = async () => {
    setLoading(true)
    try {
      const data = await getHealth()
      setStatus(data.status)
    } catch (error) {
      console.error('Health check failed:', error)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  return { status, loading, checkHealth }
}

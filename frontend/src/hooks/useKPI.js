import { useState, useEffect, useCallback, useRef } from 'react'
import { getKPIDashboard } from '../api/endpoints.js'

export function useKPI() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefreshed, setLastRefreshed] = useState(null)
  const intervalRef = useRef(null)

  const fetchData = useCallback(async () => {
    try {
      setError(null)
      const response = await getKPIDashboard()
      setData(response.data)
      setLastRefreshed(new Date())
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch KPI data')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refresh = useCallback(() => {
    setIsLoading(true)
    fetchData()
  }, [fetchData])

  useEffect(() => {
    fetchData()

    // Auto-refresh every 30 seconds
    intervalRef.current = setInterval(() => {
      fetchData()
    }, 30000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetchData])

  return {
    data,
    isLoading,
    error,
    lastRefreshed,
    refresh
  }
}

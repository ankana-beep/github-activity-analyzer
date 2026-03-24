import { useState, useCallback } from 'react'
import { getReport } from '../services/api.js'

export function useReportPoller() {
  const [polling, setPolling] = useState(false)

  const startPolling = useCallback((candidateId, onComplete, onError, interval = 2500) => {
    setPolling(true)
    let attempts = 0
    const MAX = 72 // 3 min

    const tick = async () => {
      if (++attempts > MAX) {
        setPolling(false)
        onError('Analysis timed out. Please try again.')
        return
      }
      try {
        const data = await getReport(candidateId)
        if (data.status === 'complete') { setPolling(false); onComplete(data) }
        else if (data.status === 'error') { setPolling(false); onError(data.error_message || 'Analysis failed.') }
        else setTimeout(tick, interval)
      } catch (err) {
        if (err.response?.status === 202) setTimeout(tick, interval)
        else { setPolling(false); onError(err.response?.data?.detail || 'Unexpected error.') }
      }
    }
    tick()
  }, [])

  return { polling, startPolling }
}

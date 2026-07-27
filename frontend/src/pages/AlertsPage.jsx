import { useEffect, useState } from 'react'
import AlertCard from '../components/alerts/AlertCard'
import './AlertsPage.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const POLL_INTERVAL_MS = 10000

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  async function fetchAlerts() {
    try {
      const res = await fetch(`${API_BASE}/api/alerts`)
      if (!res.ok) throw new Error(`Request failed: ${res.status}`)
      const data = await res.json()
      setAlerts(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="alerts-page">
      <header className="alerts-header">
        <div>
          <h1>Alerts</h1>
          <p className="alerts-subtitle">
            {alerts.length} alert{alerts.length !== 1 ? 's' : ''} · refreshing every 10s
          </p>
        </div>
      </header>

      {loading && <p className="alerts-empty">Loading alerts…</p>}

      {error && (
        <p className="alerts-empty alerts-error">
          Couldn't reach the backend ({error}). Is the API running?
        </p>
      )}

      {!loading && !error && alerts.length === 0 && (
        <p className="alerts-empty">No alerts yet. Trigger a detection to see it appear here.</p>
      )}

      {!loading && !error && alerts.map((alert) => (
        <AlertCard key={alert.id} alert={alert} />
      ))}
    </div>
  )
}

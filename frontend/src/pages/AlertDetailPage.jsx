import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import './AlertDetailPage.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const SEVERITY_LABELS = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

function formatTime(isoString) {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'medium',
  })
}

export default function AlertDetailPage() {
  const { id } = useParams()
  const [alert, setAlert] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchAlert() {
      try {
        const res = await fetch(`${API_BASE}/api/alerts/${id}`)
        if (!res.ok) throw new Error(`Request failed: ${res.status}`)
        const data = await res.json()
        if (data.error) throw new Error(data.error)
        setAlert(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchAlert()
  }, [id])

  if (loading) return <p className="detail-empty">Loading…</p>
  if (error) return <p className="detail-empty detail-error">Couldn't load alert ({error}).</p>
  if (!alert) return null

  const severity = alert.severity || 'low'

  return (
    <div className="detail-page">
      <Link to="/" className="detail-back">&larr; Back to alerts</Link>

      <div className={`detail-header sev-${severity}`}>
        <div className="detail-header-top">
          <span className={`alert-badge sev-${severity}`}>{SEVERITY_LABELS[severity] || severity}</span>
          <span className={`alert-status status-${alert.status}`}>{alert.status}</span>
        </div>
        <h1 className="detail-title">{alert.description}</h1>
        <p className="detail-meta">
          <span className="mono">{alert.rule_name}</span>
          <span className="detail-meta-dot">·</span>
          {formatTime(alert.created_at)}
          <span className="detail-meta-dot">·</span>
          {alert.event_count} related event{alert.event_count !== 1 ? 's' : ''}
        </p>
      </div>

      {alert.mitre_info && (
        <div className="detail-card">
          <h2 className="detail-card-title">MITRE ATT&CK Context</h2>
          <div className="detail-mitre-grid">
            <div>
              <span className="detail-label">Technique</span>
              <p className="mono">{alert.mitre_technique} — {alert.mitre_info.name}</p>
            </div>
            <div>
              <span className="detail-label">Tactic</span>
              <p>{alert.mitre_info.tactic}</p>
            </div>
          </div>
          <p className="detail-mitre-desc">{alert.mitre_info.description}</p>
          {alert.mitre_info.url && (
            <a href={alert.mitre_info.url} target="_blank" rel="noreferrer" className="detail-mitre-link">
              View on attack.mitre.org &rarr;
            </a>
          )}
        </div>
      )}

      {alert.ai_summary && (
        <div className="detail-card">
          <h2 className="detail-card-title">AI Analysis</h2>
          <p className="detail-ai-text">{alert.ai_summary}</p>
        </div>
      )}

      <div className="detail-card">
        <h2 className="detail-card-title">Related Log Events ({alert.related_events.length})</h2>
        {alert.related_events.length === 0 ? (
          <p className="detail-empty">No related events found.</p>
        ) : (
          <div className="detail-events">
            {alert.related_events.map((event) => (
              <div key={event.id} className="detail-event">
                <div className="detail-event-header">
                  <span className="mono dim">{formatTime(event.timestamp)}</span>
                  <span className="mono">{event.source_type}</span>
                  {event.source_ip && <span className="mono">{event.source_ip}</span>}
                  {event.username && <span className="mono">user: {event.username}</span>}
                  {event.host && <span className="mono">{event.host}</span>}
                </div>
                <code className="detail-event-raw">{event.raw_log}</code>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

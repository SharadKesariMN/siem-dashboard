import { Link } from 'react-router-dom'
import './AlertCard.css'

const SEVERITY_LABELS = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

function timeAgo(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime()
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function AlertCard({ alert }) {
  const severity = alert.severity || 'low'

  return (
    <Link to={`/alerts/${alert.id}`} className={`alert-card sev-${severity}`}>
      <div className="alert-card-header">
        <span className={`alert-badge sev-${severity}`}>{SEVERITY_LABELS[severity] || severity}</span>
        {alert.mitre_technique && (
          <span className="alert-mitre-tag">
            {alert.mitre_technique} - {alert.mitre_info ? alert.mitre_info.name : ''}
          </span>
        )}
        <span className="alert-time">{timeAgo(alert.created_at)}</span>
      </div>

      <h3 className="alert-title">{alert.description}</h3>

      {alert.ai_summary && (
        <p className="alert-ai-summary">{alert.ai_summary}</p>
      )}

      <div className="alert-footer">
        <span className="alert-rule">{alert.rule_name}</span>
        <span className={`alert-status status-${alert.status}`}>{alert.status}</span>
      </div>
    </Link>
  )
}

import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '../lib/api'
import './LogsPage.css'

const SEVERITY_OPTIONS = ['critical', 'high', 'medium', 'low', 'info']
const SOURCE_TYPE_OPTIONS = ['syslog', 'api', 'file']

function formatTime(isoString) {
  if (!isoString) return '-'
  const d = new Date(isoString)
  return d.toLocaleString(undefined, {
    month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}

export default function LogsPage() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [severity, setSeverity] = useState('')
  const [sourceType, setSourceType] = useState('')

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (severity) params.set('severity', severity)
      if (sourceType) params.set('source_type', sourceType)

      const data = await apiFetch(`/api/logs?${params.toString()}`)
      setLogs(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [search, severity, sourceType])

  useEffect(() => {
    const debounce = setTimeout(fetchLogs, 300)
    return () => clearTimeout(debounce)
  }, [fetchLogs])

  return (
    <div className="logs-page">
      <header className="logs-header">
        <h1>Log Explorer</h1>
        <p className="logs-subtitle">{logs.length} result{logs.length !== 1 ? 's' : ''}</p>
      </header>

      <div className="logs-toolbar">
        <input
          className="logs-search"
          type="text"
          placeholder="Search raw log, IP, user, host..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="logs-filter" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All severities</option>
          {SEVERITY_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select className="logs-filter" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
          <option value="">All sources</option>
          {SOURCE_TYPE_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {error && <p className="logs-empty logs-error">Couldn't reach the backend ({error}).</p>}
      {!error && loading && <p className="logs-empty">Loading…</p>}
      {!error && !loading && logs.length === 0 && (
        <p className="logs-empty">No logs match your filters.</p>
      )}

      {!error && !loading && logs.length > 0 && (
        <div className="logs-table-wrap">
          <table className="logs-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Source</th>
                <th>Severity</th>
                <th>Event</th>
                <th>IP</th>
                <th>User</th>
                <th>Host</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="mono dim">{formatTime(log.timestamp)}</td>
                  <td className="mono">{log.source_type}</td>
                  <td>
                    <span className={`logs-sev-dot sev-${log.severity || 'low'}`} />
                    <span className="mono">{log.severity || '-'}</span>
                  </td>
                  <td className="mono">{log.event_type || '-'}</td>
                  <td className="mono">{log.source_ip || '-'}</td>
                  <td className="mono">{log.username || '-'}</td>
                  <td className="mono">{log.host || '-'}</td>
                  <td className="logs-message" title={log.raw_log}>
                    {log.normalized_message || log.raw_log}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

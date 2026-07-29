import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { apiFetch } from '../../lib/api'
import './OverviewCharts.css'

const SEVERITY_COLORS = {
  critical: '#E5484D',
  high: '#F0883E',
  medium: '#E8C547',
  low: '#5B8DEF',
  info: '#565F73',
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="chart-tooltip">
      {payload.map((p, i) => (
        <div key={i}>{p.name}: {p.value}</div>
      ))}
    </div>
  )
}

export default function OverviewCharts() {
  const [severityData, setSeverityData] = useState([])
  const [topSources, setTopSources] = useState([])
  const [timeline, setTimeline] = useState([])

  useEffect(() => {
    async function loadStats() {
      try {
        const [sev, sources, tl] = await Promise.all([
          apiFetch('/api/stats/severity-breakdown'),
          apiFetch('/api/stats/top-sources'),
          apiFetch('/api/stats/timeline'),
        ])
        setSeverityData(Array.isArray(sev) ? sev : [])
        setTopSources(Array.isArray(sources) ? sources : [])
        setTimeline(Array.isArray(tl) ? tl : [])
      } catch (err) {
        console.error('Failed to load stats', err)
      }
    }
    loadStats()
    const interval = setInterval(loadStats, 15000)
    return () => clearInterval(interval)
  }, [])

  const hasSeverityData = severityData.some((d) => d.count > 0)

  return (
    <div className="overview-charts">
      <div className="chart-card">
        <h3 className="chart-title">Alerts by Severity</h3>
        {hasSeverityData ? (
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={severityData}
                dataKey="count"
                nameKey="severity"
                innerRadius={45}
                outerRadius={70}
                paddingAngle={3}
              >
                {severityData.map((entry, index) => (
                  <Cell key={index} fill={SEVERITY_COLORS[entry.severity] || '#565F73'} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="chart-empty">No alert data yet</p>
        )}
      </div>

      <div className="chart-card">
        <h3 className="chart-title">Top Source IPs</h3>
        {topSources.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={topSources} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="source_ip"
                width={100}
                tick={{ fill: '#8A93A6', fontSize: 12, fontFamily: 'JetBrains Mono' }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="count" fill="#3B9EFF" radius={[0, 4, 4, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="chart-empty">No source data yet</p>
        )}
      </div>

      <div className="chart-card">
        <h3 className="chart-title">Alert Volume (24h)</h3>
        {timeline.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={timeline}>
              <XAxis
                dataKey="hour"
                tick={{ fill: '#8A93A6', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis hide />
              <Tooltip content={<ChartTooltip />} />
              <Line type="monotone" dataKey="count" stroke="#3B9EFF" strokeWidth={2} dot={{ r: 3, fill: '#3B9EFF' }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="chart-empty">No timeline data yet</p>
        )}
      </div>
    </div>
  )
}

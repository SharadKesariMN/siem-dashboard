import { NavLink } from 'react-router-dom'
import './AppShell.css'

const NAV_ITEMS = [
  { to: '/', label: 'Alerts', icon: '◆' },
  { to: '/logs', label: 'Log Explorer', icon: '▤' },
]

export default function AppShell({ children }) {
  return (
    <div className="shell">
      <aside className="shell-sidebar">
        <div className="shell-brand">
          <span className="shell-brand-mark">◈</span>
          <span className="shell-brand-name">SIEM<span className="shell-brand-accent">/</span>dashboard</span>
        </div>
        <nav className="shell-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `shell-nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="shell-nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="shell-status">
          <span className="shell-live-dot" />
          Live monitoring
        </div>
      </aside>
      <main className="shell-main">{children}</main>
    </div>
  )
}

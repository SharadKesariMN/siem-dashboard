import { useState } from 'react'
import { verifyLogin, setStoredAuth } from '../lib/api'
import './LoginPage.css'

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const ok = await verifyLogin(username, password)
      if (ok) {
        setStoredAuth(username, password)
        onLogin()
      } else {
        setError('Invalid username or password')
      }
    } catch (err) {
      setError('Could not reach the backend')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-brand">
          <span className="login-brand-mark">&#9670;</span>
          <span>SIEM<span className="login-brand-accent">/</span>dashboard</span>
        </div>
        <p className="login-subtitle">Sign in to view alerts and logs</p>

        <label className="login-label">Username</label>
        <input
          className="login-input"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />

        <label className="login-label">Password</label>
        <input
          className="login-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="login-error">{error}</p>}

        <button className="login-button" type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}

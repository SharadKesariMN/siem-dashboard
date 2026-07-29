import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import AlertsPage from './pages/AlertsPage'
import AlertDetailPage from './pages/AlertDetailPage'
import LogsPage from './pages/LogsPage'
import LoginPage from './pages/LoginPage'
import { getStoredAuth } from './lib/api'
import './styles/global.css'

function App() {
  const [isAuthed, setIsAuthed] = useState(false)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    setIsAuthed(!!getStoredAuth())
    setChecked(true)
  }, [])

  if (!checked) return null

  if (!isAuthed) {
    return <LoginPage onLogin={() => setIsAuthed(true)} />
  }

  return (
    <BrowserRouter>
      <AppShell onLogout={() => setIsAuthed(false)}>
        <Routes>
          <Route path="/" element={<AlertsPage />} />
          <Route path="/alerts/:id" element={<AlertDetailPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App

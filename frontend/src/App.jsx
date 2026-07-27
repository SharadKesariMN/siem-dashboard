import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import AlertsPage from './pages/AlertsPage'
import './styles/global.css'

function LogsPagePlaceholder() {
  return <div style={{ color: 'var(--text-secondary)' }}>Log Explorer — coming in Step 11</div>
}

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<AlertsPage />} />
          <Route path="/logs" element={<LogsPagePlaceholder />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import AlertsPage from './pages/AlertsPage'
import LogsPage from './pages/LogsPage'
import './styles/global.css'

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<AlertsPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App

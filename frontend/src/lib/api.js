const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const SESSION_KEY = 'siem_auth'

export function getStoredAuth() {
  return sessionStorage.getItem(SESSION_KEY)
}

export function setStoredAuth(username, password) {
  const authHeader = 'Basic ' + btoa(`${username}:${password}`)
  sessionStorage.setItem(SESSION_KEY, authHeader)
}

export function clearStoredAuth() {
  sessionStorage.removeItem(SESSION_KEY)
}

export async function apiFetch(path) {
  const authHeader = getStoredAuth()
  const res = await fetch(`${API_BASE}${path}`, {
    headers: authHeader ? { Authorization: authHeader } : {},
  })
  if (res.status === 401) {
    clearStoredAuth()
    window.location.reload()
    throw new Error('Unauthorized')
  }
  if (!res.ok) throw new Error(`Request failed: ${res.status}`)
  return res.json()
}

export async function verifyLogin(username, password) {
  const authHeader = 'Basic ' + btoa(`${username}:${password}`)
  const res = await fetch(`${API_BASE}/api/alerts`, {
    headers: { Authorization: authHeader },
  })
  return res.ok
}

export { API_BASE }

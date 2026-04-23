/**
 * api.js — Axios client for FastAPI (plan: base URL localhost:8000).
 * In dev, Vite proxy also maps /api → backend if you prefer same-origin requests.
 */

import axios from 'axios'

const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
})

function formatError(err) {
  const d = err.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d.map(e => e.msg || JSON.stringify(e)).join('; ')
  }
  if (d && typeof d === 'object') return JSON.stringify(d)
  return err.message || 'Request failed'
}

/**
 * POST /api/predict
 */
export function predict(payload) {
  return client.post('/predict', payload).then(r => r.data).catch(e => {
    throw new Error(formatError(e))
  })
}

/**
 * GET /api/metrics
 */
export function getMetrics() {
  return client.get('/metrics').then(r => r.data).catch(e => {
    throw new Error(formatError(e))
  })
}

/**
 * GET /api/plots/list
 */
export function getPlotList() {
  return client.get('/plots/list').then(r => r.data).catch(e => {
    throw new Error(formatError(e))
  })
}

/**
 * GET /api/health
 */
export function getHealth() {
  return client.get('/health').then(r => r.data).catch(e => {
    throw new Error(formatError(e))
  })
}

export { API_BASE }

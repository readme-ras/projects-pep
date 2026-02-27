const BASE = import.meta.env.VITE_API_URL || '/api'

async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(`${BASE}${path}`, opts)
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export const api = {
  listTasks:      (params = {}) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => v != null && q.set(k, v))
    const qs = q.toString()
    return req('GET', `/tasks${qs ? '?' + qs : ''}`)
  },
  createTask:     (body)     => req('POST',   '/tasks', body),
  updateTask:     (id, body) => req('PUT',    `/tasks/${id}`, body),
  toggleComplete: (id)       => req('PATCH',  `/tasks/${id}/complete`),
  deleteTask:     (id)       => req('DELETE', `/tasks/${id}`),
  stats:          ()         => req('GET',    '/tasks/stats/summary'),
}

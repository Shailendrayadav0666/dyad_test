const BASE = '/api'

async function handleResponse(res) {
  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.message || json.detail || 'Request failed')
  }
  return json
}

export async function uploadPdf(file) {
  const form = new FormData()
  form.append('file', file)
  return handleResponse(await fetch(`${BASE}/upload`, { method: 'POST', body: form }))
}

export async function getStatus(sessionId) {
  return handleResponse(await fetch(`${BASE}/status/${sessionId}`))
}

export async function getAnswer(sessionId, query) {
  return handleResponse(
    await fetch(`${BASE}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, query }),
    })
  )
}

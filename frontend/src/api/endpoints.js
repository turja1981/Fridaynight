import apiClient from './client.js'

export const login = (username, password) =>
  apiClient.post('/auth/login', { username, password })

export const getCurrentUser = () =>
  apiClient.get('/auth/me')

export const sendChat = (message, adapter, sessionId) =>
  apiClient.post('/chat', { message, adapter, session_id: sessionId })

export const getKPIDashboard = () =>
  apiClient.get('/kpi/dashboard')

export const ingestDocument = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return apiClient.post('/rag/ingest', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const analyzeImage = (file, task) => {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('task', task)
  return apiClient.post('/multimodal/analyze', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const queryRAG = (query, topK = 5) =>
  apiClient.post('/rag/query', { query, top_k: topK })

export const runAgent = (task, agentType = 'auto') =>
  apiClient.post('/agents/run', { task, agent_type: agentType })

export const transcribeVoice = (audioBlob) => {
  const fd = new FormData()
  fd.append('audio', audioBlob, 'recording.webm')
  return apiClient.post('/voice/transcribe', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

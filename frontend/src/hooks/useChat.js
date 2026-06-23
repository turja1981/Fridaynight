import { useState, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { sendChat, analyzeImage } from '../api/endpoints.js'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => uuidv4())

  const sendMessage = useCallback(async (text, adapter = 'default', imageFile = null) => {
    let finalMessage = text

    // If image is attached, analyze it first and prepend analysis
    if (imageFile) {
      try {
        const imageResponse = await analyzeImage(imageFile, 'describe')
        const analysis = imageResponse.data?.analysis || imageResponse.data?.description || ''
        if (analysis) {
          finalMessage = `[Image Analysis: ${analysis}]\n\n${text}`
        }
      } catch (err) {
        console.error('Image analysis failed:', err)
      }
    }

    // Add user message to the list
    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: text,
      imageFile: imageFile ? URL.createObjectURL(imageFile) : null,
      timestamp: new Date().toISOString()
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    const startTime = performance.now()

    try {
      const response = await sendChat(finalMessage, adapter, sessionId)
      const endTime = performance.now()
      const latencyMs = Math.round(endTime - startTime)

      const data = response.data
      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: data.response || data.message || data.content || '',
        metadata: {
          latency: latencyMs,
          tokens: data.usage?.total_tokens || data.tokens || null,
          model: data.model || null,
          tool_calls: data.tool_calls || data.agent_steps || []
        },
        timestamp: new Date().toISOString()
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || err.message || 'Something went wrong. Please try again.'}`,
        isError: true,
        metadata: {
          latency: Math.round(performance.now() - startTime),
          tokens: null,
          model: null,
          tool_calls: []
        },
        timestamp: new Date().toISOString()
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const sendMessageStreaming = useCallback(async (text, adapter = 'default') => {
    const userMsg = { role: 'user', content: text, id: uuidv4(), timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])

    // Add placeholder assistant message
    const assistantId = uuidv4()
    setMessages(prev => [...prev, { role: 'assistant', content: '', id: assistantId, streaming: true, timestamp: new Date().toISOString() }])
    setIsLoading(true)

    try {
      const token = localStorage.getItem('eap_token')
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: text, adapter, session_id: sessionId }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let metadata = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'token') {
              setMessages(prev => prev.map(m =>
                m.id === assistantId ? { ...m, content: m.content + event.chunk } : m
              ))
            } else if (event.type === 'tool_start') {
              setMessages(prev => prev.map(m =>
                m.id === assistantId ? { ...m, activeToolCall: event.tool } : m
              ))
            } else if (event.type === 'tool_end') {
              setMessages(prev => prev.map(m =>
                m.id === assistantId ? { ...m, activeToolCall: null } : m
              ))
            } else if (event.type === 'done') {
              metadata = event.metadata
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, streaming: false, activeToolCall: null, metadata: {
                      latency: metadata.latency_ms,
                      model: metadata.model_used,
                      tool_calls: metadata.tool_calls || [],
                      tokens: null,
                    }}
                  : m
              ))
            } else if (event.type === 'error') {
              setMessages(prev => prev.map(m =>
                m.id === assistantId ? { ...m, content: `Error: ${event.message}`, streaming: false, isError: true, activeToolCall: null } : m
              ))
            }
          } catch {}
        }
      }
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === assistantId ? { ...m, content: 'Connection error. Please try again.', streaming: false, isError: true, activeToolCall: null } : m
      ))
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const clearChat = useCallback(() => {
    setMessages([])
  }, [])

  return {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    sendMessageStreaming,
    clearChat
  }
}

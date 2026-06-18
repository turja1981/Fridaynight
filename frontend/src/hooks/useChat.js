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

  const clearChat = useCallback(() => {
    setMessages([])
  }, [])

  return {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    clearChat
  }
}

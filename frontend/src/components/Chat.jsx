import React, { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Send,
  Paperclip,
  X,
  Image,
  Cpu,
  Zap,
  Hash,
  Clock,
  Trash2
} from 'lucide-react'
import { useChat } from '../hooks/useChat.js'
import FileUpload from './FileUpload.jsx'
import VoiceInput from './VoiceInput.jsx'
import AgentStatus from './AgentStatus.jsx'

function MessageBadge({ children, color = 'gray' }) {
  const colorMap = {
    gray: 'bg-gray-800 text-gray-400 border-gray-700',
    indigo: 'bg-indigo-950 text-indigo-400 border-indigo-800',
    emerald: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    amber: 'bg-amber-950 text-amber-400 border-amber-800'
  }
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 border rounded text-xs font-medium ${colorMap[color]}`}>
      {children}
    </span>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-4 message-enter">
      <div className="w-7 h-7 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center flex-shrink-0">
        <Cpu className="w-3.5 h-3.5 text-indigo-400" />
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-none px-4 py-3">
        <div className="typing-dots">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  )
}

function UserMessage({ msg }) {
  return (
    <div className="flex justify-end mb-4 message-enter">
      <div className="max-w-[75%]">
        {msg.imageFile && (
          <div className="mb-2 flex justify-end">
            <img
              src={msg.imageFile}
              alt="Attached"
              className="max-h-40 rounded-lg border border-gray-700 object-contain"
            />
          </div>
        )}
        <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-none px-4 py-2.5 text-sm leading-relaxed">
          {msg.content}
        </div>
      </div>
    </div>
  )
}

function AssistantMessage({ msg }) {
  const meta = msg.metadata || {}
  const toolCalls = meta.tool_calls || []

  return (
    <div className="flex items-start gap-3 mb-4 message-enter">
      <div className="w-7 h-7 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Cpu className="w-3.5 h-3.5 text-indigo-400" />
      </div>
      <div className="max-w-[80%] flex-1">
        <div className={`border rounded-2xl rounded-tl-none px-4 py-3 text-sm leading-relaxed
          ${msg.isError
            ? 'bg-red-950 border-red-800 text-red-300'
            : 'bg-gray-800 border-gray-700 text-gray-100'}`}
        >
          <div className="prose prose-invert prose-sm max-w-none
            prose-p:my-1 prose-headings:text-gray-100 prose-code:text-indigo-300
            prose-code:bg-gray-900 prose-code:px-1 prose-code:rounded
            prose-pre:bg-gray-900 prose-pre:border prose-pre:border-gray-700
            prose-a:text-indigo-400 prose-strong:text-gray-100
            prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        </div>

        {/* Metadata footer */}
        {!msg.isError && (meta.model || meta.latency || meta.tokens) && (
          <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
            {meta.model && (
              <MessageBadge color="indigo">
                <Zap className="w-2.5 h-2.5" />
                {meta.model}
              </MessageBadge>
            )}
            {meta.latency != null && (
              <MessageBadge color="gray">
                <Clock className="w-2.5 h-2.5" />
                {meta.latency}ms
              </MessageBadge>
            )}
            {meta.tokens != null && (
              <MessageBadge color="gray">
                <Hash className="w-2.5 h-2.5" />
                {meta.tokens} tokens
              </MessageBadge>
            )}
            {toolCalls.length > 0 && (
              <MessageBadge color="amber">
                <Cpu className="w-2.5 h-2.5" />
                {toolCalls.length} tool{toolCalls.length !== 1 ? 's' : ''}
              </MessageBadge>
            )}
          </div>
        )}

        {/* Agent tool calls */}
        <AgentStatus toolCalls={toolCalls} />
      </div>
    </div>
  )
}

function EmptyState({ adapter }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="w-14 h-14 rounded-2xl bg-gray-900 border border-gray-800 flex items-center justify-center mb-4">
        <Cpu className="w-7 h-7 text-indigo-500" />
      </div>
      <h3 className="text-base font-semibold text-gray-200 mb-1">
        Enterprise AI Assistant
      </h3>
      <p className="text-sm text-gray-500 max-w-sm">
        Ask anything. Attach documents for analysis, use voice input, or start a conversation.
        {adapter && adapter !== 'default' && (
          <span className="block mt-1 text-indigo-400">Using adapter: {adapter}</span>
        )}
      </p>
      <div className="mt-6 grid grid-cols-2 gap-2 max-w-sm w-full">
        {[
          'Summarize the Q3 financial report',
          'What are the key risks in this contract?',
          'Analyze customer sentiment trends',
          'Draft an executive summary'
        ].map((suggestion) => (
          <button
            key={suggestion}
            className="px-3 py-2.5 bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-gray-700
              rounded-lg text-xs text-gray-400 hover:text-gray-300 text-left transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function Chat({ adapter = 'default' }) {
  const { messages, isLoading, sendMessage, clearChat } = useChat()
  const [inputText, setInputText] = useState('')
  const [attachedImage, setAttachedImage] = useState(null)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [fileUploadMode, setFileUploadMode] = useState('document')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (ta) {
      ta.style.height = 'auto'
      ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
    }
  }, [inputText])

  const handleSend = useCallback(async () => {
    const text = inputText.trim()
    if (!text || isLoading) return

    const imageToSend = attachedImage
    setInputText('')
    setAttachedImage(null)

    await sendMessage(text, adapter, imageToSend)
  }, [inputText, isLoading, attachedImage, sendMessage, adapter])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleVoiceTranscript = (text) => {
    setInputText((prev) => prev ? `${prev} ${text}` : text)
    textareaRef.current?.focus()
  }

  const handleFileProcessed = ({ file, result, mode }) => {
    if (mode === 'image') {
      setAttachedImage(file)
    } else {
      // Document ingested — add a system notification message
      const notification = result?.message || `Document "${file.name}" ingested successfully.`
      sendMessage(`[Document uploaded: ${file.name}]\n${notification}`, adapter, null)
    }
  }

  const openImageUpload = () => {
    setFileUploadMode('image')
    setShowFileUpload(true)
  }

  const openDocUpload = () => {
    setFileUploadMode('document')
    setShowFileUpload(true)
  }

  const canSend = inputText.trim().length > 0 && !isLoading

  return (
    <div className="flex flex-col h-full bg-gray-950">
      {/* Chat header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-900 flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">Conversation</span>
          {messages.length > 0 && (
            <span className="px-1.5 py-0.5 bg-gray-800 text-gray-500 text-xs rounded">
              {messages.length} messages
            </span>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-500 hover:text-gray-300
              hover:bg-gray-800 rounded-lg transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Clear
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.length === 0 && !isLoading ? (
          <EmptyState adapter={adapter} />
        ) : (
          <>
            {messages.map((msg) =>
              msg.role === 'user' ? (
                <UserMessage key={msg.id} msg={msg} />
              ) : (
                <AssistantMessage key={msg.id} msg={msg} />
              )
            )}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <div className="flex-shrink-0 border-t border-gray-800 bg-gray-900 px-4 py-3">
        {/* Image attachment preview */}
        {attachedImage && (
          <div className="flex items-center gap-2 mb-2 px-1">
            <div className="relative group">
              <img
                src={URL.createObjectURL(attachedImage)}
                alt="Attached"
                className="h-14 w-14 object-cover rounded-lg border border-gray-700"
              />
              <button
                onClick={() => setAttachedImage(null)}
                className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 rounded-full flex items-center justify-center
                  opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-2.5 h-2.5 text-white" />
              </button>
            </div>
            <span className="text-xs text-gray-500">{attachedImage.name}</span>
          </div>
        )}

        <div className="flex items-end gap-2">
          {/* Attachment buttons */}
          <div className="flex items-center gap-1 pb-1">
            <button
              onClick={openDocUpload}
              className="p-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
              title="Attach document"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <button
              onClick={openImageUpload}
              className="p-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
              title="Attach image"
            >
              <Image className="w-5 h-5" />
            </button>
          </div>

          {/* Text input */}
          <div className="flex-1 bg-gray-800 border border-gray-700 focus-within:border-indigo-500
            focus-within:ring-1 focus-within:ring-indigo-500 rounded-xl transition-colors">
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
              rows={1}
              disabled={isLoading}
              className="w-full bg-transparent text-gray-100 placeholder-gray-600 text-sm
                px-3 py-2.5 resize-none focus:outline-none disabled:opacity-50
                min-h-[44px] max-h-[160px]"
              style={{ lineHeight: '1.5' }}
            />
          </div>

          {/* Voice input */}
          <div className="pb-1">
            <VoiceInput onTranscript={handleVoiceTranscript} />
          </div>

          {/* Send button */}
          <div className="pb-1">
            <button
              onClick={handleSend}
              disabled={!canSend}
              className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500
                disabled:bg-gray-800 disabled:text-gray-600 disabled:cursor-not-allowed
                text-white transition-colors"
              title="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        <p className="text-xs text-gray-700 mt-1.5 px-1">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>

      {/* File Upload Modal */}
      {showFileUpload && (
        <FileUpload
          mode={fileUploadMode}
          onClose={() => setShowFileUpload(false)}
          onFileProcessed={(result) => {
            handleFileProcessed(result)
            setShowFileUpload(false)
          }}
        />
      )}
    </div>
  )
}

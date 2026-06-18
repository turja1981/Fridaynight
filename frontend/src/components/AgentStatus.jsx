import React, { useState } from 'react'
import { ChevronDown, ChevronRight, CheckCircle, XCircle, Clock } from 'lucide-react'

function ToolCallRow({ call, index }) {
  const [expanded, setExpanded] = useState(false)

  const isSuccess = !call.error
  const toolName = call.tool_name || call.tool || `Step ${index + 1}`
  const duration = call.duration_ms != null ? call.duration_ms : null
  const inputData = call.input || call.parameters || {}
  const outputData = call.output || call.result || null

  const inputPreview = typeof inputData === 'string'
    ? inputData.slice(0, 80)
    : JSON.stringify(inputData).slice(0, 80)

  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-800 transition-colors text-left"
      >
        {/* Status dot */}
        {isSuccess ? (
          <CheckCircle className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
        ) : (
          <XCircle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
        )}

        {/* Tool name */}
        <span className="px-2 py-0.5 bg-indigo-950 text-indigo-300 border border-indigo-800 rounded text-xs font-mono font-medium flex-shrink-0">
          {toolName}
        </span>

        {/* Input preview */}
        <span className="text-xs text-gray-500 truncate flex-1 font-mono">
          {inputPreview}{inputPreview.length >= 80 ? '...' : ''}
        </span>

        {/* Duration */}
        {duration != null && (
          <span className="flex items-center gap-1 text-xs text-gray-600 flex-shrink-0">
            <Clock className="w-3 h-3" />
            {duration}ms
          </span>
        )}

        {/* Expand chevron */}
        {expanded ? (
          <ChevronDown className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" />
        )}
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="border-t border-gray-800 bg-gray-950 px-3 py-2 space-y-2">
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">Input</p>
            <pre className="text-xs text-gray-300 bg-gray-900 border border-gray-800 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
              {typeof inputData === 'string' ? inputData : JSON.stringify(inputData, null, 2)}
            </pre>
          </div>
          {outputData != null && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Output</p>
              <pre className="text-xs text-gray-300 bg-gray-900 border border-gray-800 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
                {typeof outputData === 'string' ? outputData : JSON.stringify(outputData, null, 2)}
              </pre>
            </div>
          )}
          {call.error && (
            <div>
              <p className="text-xs font-medium text-red-500 mb-1">Error</p>
              <pre className="text-xs text-red-400 bg-red-950 border border-red-900 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
                {typeof call.error === 'string' ? call.error : JSON.stringify(call.error, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function AgentStatus({ toolCalls }) {
  const [collapsed, setCollapsed] = useState(false)

  if (!toolCalls || toolCalls.length === 0) return null

  return (
    <div className="mt-2 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-gray-850 hover:bg-gray-800 transition-colors text-left"
        style={{ backgroundColor: 'rgba(17,24,39,0.8)' }}
      >
        {collapsed ? (
          <ChevronRight className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
        )}
        <span className="text-xs font-medium text-gray-400">
          Agent Activity
        </span>
        <span className="px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded text-xs">
          {toolCalls.length} {toolCalls.length === 1 ? 'step' : 'steps'}
        </span>
      </button>

      {!collapsed && (
        <div className="px-3 py-2 space-y-1.5 bg-gray-950">
          {toolCalls.map((call, index) => (
            <ToolCallRow key={index} call={call} index={index} />
          ))}
        </div>
      )}
    </div>
  )
}

'use client'
import React, { useState } from 'react'
import { Hexagon, MessageSquare, LayoutDashboard, LogOut, ChevronDown } from 'lucide-react'
import { useAuth } from './hooks/useAuth.js'
import LoginPage from './components/LoginPage.jsx'
import Chat from './components/Chat.jsx'
import KPIDashboard from './components/KPIDashboard.jsx'

const ADAPTERS = [
  { value: 'default', label: 'Default' },
  { value: 'rag', label: 'RAG (Document QA)' },
  { value: 'agent', label: 'Agent (Autonomous)' },
  { value: 'multimodal', label: 'Multimodal' },
  { value: 'analyst', label: 'Business Analyst' }
]

const ROLE_STYLES = {
  admin: 'bg-red-900 text-red-300 border-red-800',
  analyst: 'bg-amber-900 text-amber-300 border-amber-800',
  viewer: 'bg-emerald-900 text-emerald-300 border-emerald-800'
}

function UserBadge({ user }) {
  if (!user) return null
  const role = (user.role || 'viewer').toLowerCase()
  const style = ROLE_STYLES[role] || ROLE_STYLES.viewer

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-300 hidden sm:block">{user.username || user.name}</span>
      <span className={`px-2 py-0.5 border rounded text-xs font-semibold uppercase tracking-wide ${style}`}>
        {role}
      </span>
    </div>
  )
}

function AdapterSelector({ value, onChange }) {
  const current = ADAPTERS.find((a) => a.value === value) || ADAPTERS[0]

  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none pl-3 pr-8 py-1.5 bg-gray-800 border border-gray-700
          hover:border-gray-600 text-gray-300 text-xs rounded-lg cursor-pointer
          focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500
          transition-colors"
      >
        {ADAPTERS.map((a) => (
          <option key={a.value} value={a.value}>
            {a.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
    </div>
  )
}

export default function App() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()
  const [activeTab, setActiveTab] = useState('chat')
  const [activeAdapter, setActiveAdapter] = useState('default')

  // Show loading spinner while restoring session
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Hexagon className="w-10 h-10 text-indigo-500 animate-pulse" strokeWidth={1.5} />
          <p className="text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={login} />
  }

  return (
    <div className="h-screen bg-gray-950 flex flex-col overflow-hidden">
      {/* Top Navigation Bar */}
      <header className="flex-shrink-0 h-14 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-4">
        {/* Left: Logo */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Hexagon className="w-6 h-6 text-indigo-500" strokeWidth={1.5} />
          <div className="leading-tight">
            <span className="text-sm font-bold text-indigo-400 tracking-tight">TCS Enterprise AI</span>
            <p className="text-xs text-gray-600 leading-none">Powered by Claude</p>
          </div>
        </div>

        {/* Center: Tab buttons */}
        <div className="flex-1 flex items-center justify-center">
          <div className="flex items-center bg-gray-800 rounded-lg p-0.5 gap-0.5">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                ${activeTab === 'chat'
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'}`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Chat
            </button>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                ${activeTab === 'dashboard'
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'}`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              Dashboard
            </button>
          </div>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {activeTab === 'chat' && (
            <AdapterSelector value={activeAdapter} onChange={setActiveAdapter} />
          )}
          <UserBadge user={user} />
          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-500
              hover:text-gray-200 hover:bg-gray-800 border border-transparent
              hover:border-gray-700 rounded-lg transition-colors"
            title="Sign out"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? (
          <Chat adapter={activeAdapter} />
        ) : (
          <KPIDashboard />
        )}
      </main>

      {/* Bottom Status Bar */}
      <footer className="flex-shrink-0 h-7 bg-gray-900 border-t border-gray-800 flex items-center px-4 gap-4">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="text-xs text-gray-600">Connected</span>
        </div>
        <span className="text-gray-800">|</span>
        <span className="text-xs text-gray-600">Model: claude-sonnet-4-6</span>
        <span className="text-gray-800">|</span>
        <span className="text-xs text-gray-600">v1.0.0</span>
        {activeTab === 'chat' && activeAdapter !== 'default' && (
          <>
            <span className="text-gray-800">|</span>
            <span className="text-xs text-indigo-500">Adapter: {activeAdapter}</span>
          </>
        )}
      </footer>
    </div>
  )
}

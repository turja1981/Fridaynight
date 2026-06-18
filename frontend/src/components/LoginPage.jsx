import React, { useState } from 'react'
import { Loader2, AlertCircle, Hexagon } from 'lucide-react'

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.')
      return
    }
    setIsLoading(true)
    setError('')
    try {
      await onLogin(username.trim(), password)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Invalid credentials. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Hexagon className="w-10 h-10 text-indigo-500" strokeWidth={1.5} />
            <span className="text-2xl font-bold text-white tracking-tight">TCS</span>
          </div>
          <h1 className="text-xl font-semibold text-gray-100">Enterprise AI Platform</h1>
          <p className="text-sm text-gray-500 mt-1">Powered by Claude</p>
        </div>

        {/* Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl">
          <h2 className="text-lg font-medium text-gray-100 mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error message */}
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-950 border border-red-800 rounded-lg text-red-400 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-400 mb-1.5">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                autoComplete="username"
                disabled={isLoading}
                className={`w-full px-3 py-2.5 bg-gray-800 border rounded-lg text-gray-100 placeholder-gray-600 text-sm
                  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors
                  ${error ? 'border-red-700' : 'border-gray-700 hover:border-gray-600'}`}
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-400 mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={isLoading}
                className={`w-full px-3 py-2.5 bg-gray-800 border rounded-lg text-gray-100 placeholder-gray-600 text-sm
                  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors
                  ${error ? 'border-red-700' : 'border-gray-700 hover:border-gray-600'}`}
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || !username.trim() || !password.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-indigo-600
                hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed
                text-white font-medium rounded-lg text-sm transition-colors mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 pt-5 border-t border-gray-800">
            <p className="text-xs text-gray-600 text-center mb-2">Demo Credentials</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              {[
                { user: 'admin', pass: 'admin123', role: 'Admin' },
                { user: 'analyst', pass: 'analyst123', role: 'Analyst' },
                { user: 'viewer', pass: 'viewer123', role: 'Viewer' }
              ].map(({ user, pass, role }) => (
                <button
                  key={user}
                  type="button"
                  onClick={() => {
                    setUsername(user)
                    setPassword(pass)
                    setError('')
                  }}
                  className="px-2 py-1.5 bg-gray-800 hover:bg-gray-750 border border-gray-700
                    rounded-md text-xs text-gray-400 hover:text-gray-300 transition-colors"
                >
                  <div className="font-medium text-gray-300">{role}</div>
                  <div className="text-gray-600 mt-0.5">{user}</div>
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-700 text-center mt-2">
              Click a role to auto-fill credentials
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-700 mt-6">
          TCS Enterprise AI Platform v1.0.0
        </p>
      </div>
    </div>
  )
}

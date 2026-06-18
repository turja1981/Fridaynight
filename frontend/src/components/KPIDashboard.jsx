import React from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts'
import {
  TrendingUp, TrendingDown, Minus,
  CheckCircle, AlertTriangle, XCircle,
  RefreshCw, Clock, DollarSign, Activity,
  MessageSquare, Zap, BarChart2, Users
} from 'lucide-react'
import { useKPI } from '../hooks/useKPI.js'

// ---- Skeleton loading card ----
function SkeletonCard() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="skeleton-pulse h-4 w-24 mb-3" />
      <div className="skeleton-pulse h-8 w-32 mb-2" />
      <div className="skeleton-pulse h-3 w-16" />
    </div>
  )
}

function SkeletonChart({ height = 220 }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="skeleton-pulse h-4 w-36 mb-4" />
      <div className="skeleton-pulse rounded-lg" style={{ height }} />
    </div>
  )
}

// ---- Metric Card ----
function MetricCard({ title, value, unit = '', trend, trendValue, status, icon: Icon }) {
  const statusColors = {
    good: 'text-emerald-400',
    warning: 'text-amber-400',
    bad: 'text-red-400',
    neutral: 'text-gray-400'
  }

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-red-400' : 'text-gray-500'

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</span>
        {Icon && <Icon className="w-4 h-4 text-gray-600" />}
      </div>
      <div className="flex items-end gap-2 mb-1">
        <span className={`text-2xl font-bold ${statusColors[status] || 'text-gray-100'}`}>
          {value}
        </span>
        {unit && <span className="text-sm text-gray-500 mb-0.5">{unit}</span>}
      </div>
      {trendValue != null && (
        <div className={`flex items-center gap-1 text-xs ${trendColor}`}>
          <TrendIcon className="w-3 h-3" />
          <span>{trendValue}</span>
        </div>
      )}
    </div>
  )
}

// ---- Custom chart tooltip ----
const DarkTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 shadow-xl">
      {label && <p className="text-xs text-gray-500 mb-1">{label}</p>}
      {payload.map((entry, i) => (
        <p key={i} className="text-xs font-medium" style={{ color: entry.color }}>
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  )
}

const CHART_COLORS = ['#6366f1', '#22d3ee', '#a78bfa', '#34d399', '#fb923c', '#f472b6']
const MODEL_COLORS = {
  'claude-haiku': '#22d3ee',
  'claude-sonnet': '#6366f1',
  'claude-opus': '#a78bfa',
  haiku: '#22d3ee',
  sonnet: '#6366f1',
  opus: '#a78bfa'
}

// Fallback/demo data if backend doesn't return structured data
function buildFallbackData() {
  const now = new Date()
  const hours = Array.from({ length: 24 }, (_, i) => {
    const h = new Date(now)
    h.setHours(h.getHours() - 23 + i)
    return {
      time: `${h.getHours()}:00`,
      queries: Math.floor(Math.random() * 120) + 10
    }
  })
  return {
    summary: {
      total_queries: 2847,
      success_rate: 96.4,
      avg_latency_ms: 742,
      cost_estimate: 12.34
    },
    queries_over_time: hours,
    agent_usage: [
      { agent: 'Research', count: 412 },
      { agent: 'Analysis', count: 287 },
      { agent: 'RAG', count: 634 },
      { agent: 'Code', count: 198 },
      { agent: 'General', count: 923 }
    ],
    model_distribution: [
      { name: 'claude-sonnet', value: 58 },
      { name: 'claude-haiku', value: 30 },
      { name: 'claude-opus', value: 12 }
    ],
    business_kpis: [
      { domain: 'Finance', metric: 'Reports Analyzed', value: '148', change: '+12%', status: 'good' },
      { domain: 'Legal', metric: 'Contracts Reviewed', value: '67', change: '+5%', status: 'good' },
      { domain: 'HR', metric: 'Resumes Screened', value: '312', change: '+23%', status: 'good' },
      { domain: 'Sales', metric: 'Leads Qualified', value: '89', change: '-3%', status: 'warning' },
      { domain: 'Support', metric: 'Tickets Resolved', value: '1,204', change: '+18%', status: 'good' },
      { domain: 'R&D', metric: 'Patents Reviewed', value: '24', change: '0%', status: 'neutral' }
    ]
  }
}

export default function KPIDashboard() {
  const { data: rawData, isLoading, error, lastRefreshed, refresh } = useKPI()

  const data = rawData || (isLoading ? null : buildFallbackData())

  const formatTimestamp = (date) => {
    if (!date) return 'Never'
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  const getSuccessStatus = (rate) => {
    if (rate >= 90) return 'good'
    if (rate >= 70) return 'warning'
    return 'bad'
  }

  const getLatencyStatus = (ms) => {
    if (ms < 1000) return 'good'
    if (ms < 2000) return 'warning'
    return 'bad'
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-950 px-4 py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">KPI Dashboard</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Last updated: {formatTimestamp(lastRefreshed)}
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700
            border border-gray-700 text-gray-300 text-xs rounded-lg transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Error state */}
      {error && !data && (
        <div className="bg-red-950 border border-red-800 rounded-xl p-4 mb-5 text-red-400 text-sm">
          Failed to load KPI data: {error}
        </div>
      )}

      {/* Row 1: Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {isLoading && !data ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : data ? (
          <>
            <MetricCard
              title="Total Queries"
              value={(data.summary?.total_queries ?? 0).toLocaleString()}
              trend="up"
              trendValue="+8% vs yesterday"
              status="neutral"
              icon={MessageSquare}
            />
            <MetricCard
              title="Success Rate"
              value={`${(data.summary?.success_rate ?? 0).toFixed(1)}`}
              unit="%"
              trend={data.summary?.success_rate >= 90 ? 'up' : 'down'}
              trendValue={data.summary?.success_rate >= 90 ? 'On target' : 'Below target'}
              status={getSuccessStatus(data.summary?.success_rate ?? 0)}
              icon={CheckCircle}
            />
            <MetricCard
              title="Avg Latency"
              value={(data.summary?.avg_latency_ms ?? 0).toLocaleString()}
              unit="ms"
              trend={data.summary?.avg_latency_ms < 1000 ? 'down' : 'up'}
              trendValue={data.summary?.avg_latency_ms < 1000 ? 'Good' : 'High'}
              status={getLatencyStatus(data.summary?.avg_latency_ms ?? 9999)}
              icon={Zap}
            />
            <MetricCard
              title="Cost Estimate"
              value={`$${(data.summary?.cost_estimate ?? 0).toFixed(2)}`}
              trend="neutral"
              trendValue="Today"
              status="neutral"
              icon={DollarSign}
            />
          </>
        ) : null}
      </div>

      {/* Row 2: Line Chart - Queries over time */}
      {isLoading && !data ? (
        <SkeletonChart height={220} />
      ) : data?.queries_over_time?.length > 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-5">
          <h3 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" />
            Query Volume (Last 24 Hours)
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data.queries_over_time} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fill: '#6b7280', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fill: '#6b7280', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<DarkTooltip />} />
              <Line
                type="monotone"
                dataKey="queries"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#6366f1' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : null}

      {/* Row 3: Bar + Pie */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-5">
        {/* Agent Usage Bar Chart */}
        {isLoading && !data ? (
          <SkeletonChart height={200} />
        ) : data?.agent_usage?.length > 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-indigo-400" />
              Agent Usage Breakdown
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={data.agent_usage} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="agent"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<DarkTooltip />} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {data.agent_usage.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : null}

        {/* Model Distribution Pie Chart */}
        {isLoading && !data ? (
          <SkeletonChart height={200} />
        ) : data?.model_distribution?.length > 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-indigo-400" />
              Model Distribution
            </h3>
            <div className="flex items-center gap-4">
              <ResponsiveContainer width="60%" height={180}>
                <PieChart>
                  <Pie
                    data={data.model_distribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {data.model_distribution.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={MODEL_COLORS[entry.name] || CHART_COLORS[index % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<DarkTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-col gap-2">
                {data.model_distribution.map((entry, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{
                        backgroundColor: MODEL_COLORS[entry.name] || CHART_COLORS[index % CHART_COLORS.length]
                      }}
                    />
                    <div>
                      <p className="text-xs text-gray-300 font-medium">{entry.name}</p>
                      <p className="text-xs text-gray-600">{entry.value}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Row 4: Business KPIs Table */}
      {data?.business_kpis?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden mb-5">
          <div className="px-5 py-3 border-b border-gray-800">
            <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <Users className="w-4 h-4 text-indigo-400" />
              Business KPIs by Domain
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-5 py-3 text-left font-medium">Domain</th>
                  <th className="px-5 py-3 text-left font-medium">Metric</th>
                  <th className="px-5 py-3 text-right font-medium">Value</th>
                  <th className="px-5 py-3 text-right font-medium">Change</th>
                  <th className="px-5 py-3 text-center font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {data.business_kpis.map((kpi, index) => {
                  const StatusIcon =
                    kpi.status === 'good' ? CheckCircle :
                    kpi.status === 'warning' ? AlertTriangle : XCircle
                  const statusColor =
                    kpi.status === 'good' ? 'text-emerald-400' :
                    kpi.status === 'warning' ? 'text-amber-400' :
                    kpi.status === 'bad' ? 'text-red-400' : 'text-gray-500'
                  const changeColor = kpi.change?.startsWith('+') ? 'text-emerald-400' :
                    kpi.change?.startsWith('-') ? 'text-red-400' : 'text-gray-500'

                  return (
                    <tr key={index} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-5 py-3">
                        <span className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded font-medium">
                          {kpi.domain}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-sm text-gray-300">{kpi.metric}</td>
                      <td className="px-5 py-3 text-sm text-gray-100 text-right font-semibold">{kpi.value}</td>
                      <td className={`px-5 py-3 text-xs text-right font-medium ${changeColor}`}>
                        {kpi.change}
                      </td>
                      <td className="px-5 py-3 text-center">
                        <StatusIcon className={`w-4 h-4 ${statusColor} inline`} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Auto-refresh indicator */}
      <div className="flex items-center justify-center gap-1.5 text-xs text-gray-700 pb-2">
        <Clock className="w-3 h-3" />
        Auto-refreshes every 30 seconds
      </div>
    </div>
  )
}

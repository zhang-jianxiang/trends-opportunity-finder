import {
  getTrendColor, getTrendIcon, getPotentialColor, getPotentialLabel,
  formatScore, getOpportunityTypeLabel, getOpportunityTypeColor, formatDate
} from '@/lib/utils'
import { TrendingUp, Target, AlertTriangle, Database, ArrowRight } from 'lucide-react'
import Link from 'next/link'

async function getDashboardData(): Promise<any> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/dashboard`, {
      cache: 'no-store'
    })
    if (!res.ok) throw new Error('Failed to fetch')
    return await res.json()
  } catch {
    return {
      stats: { keywordCount: 0, dataCount: 0, anomalyCount: 0, opportunityCount: 0 },
      opportunities: [],
      analysis: [],
      logs: []
    }
  }
}

export default async function DashboardPage() {
  const { stats, opportunities, analysis, logs } = await getDashboardData()

  const statCards = [
    { label: '监控关键词', value: stats.keywordCount || 0, icon: Database, color: 'text-primary' },
    { label: '活跃机会', value: stats.opportunityCount || 0, icon: Target, color: 'text-success' },
    { label: '异常趋势', value: stats.anomalyCount || 0, icon: AlertTriangle, color: 'text-warning' },
    { label: '数据记录', value: stats.dataCount || 0, icon: TrendingUp, color: 'text-accent' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">市场趋势仪表板</h1>
        <p className="text-sm text-zinc-500 mt-1">实时监控 Google Trends 数据和市场机会</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-surface border border-border rounded-xl p-5 animate-fade-in">
            <div className="flex items-center justify-between mb-3">
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div className="text-3xl font-bold">{stat.value.toLocaleString()}</div>
            <div className="text-xs text-zinc-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最新机会 */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Target className="w-4 h-4 text-success" />
              最新市场机会
            </h2>
            <Link href="/opportunities" className="text-xs text-zinc-500 hover:text-primary flex items-center gap-1">
              查看全部 <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-3">
            {opportunities && opportunities.length > 0 ? (
              opportunities.map((opp: any) => (
                <div key={opp.id} className="flex items-start justify-between p-3 rounded-lg bg-zinc-800/30 border border-zinc-700/30 hover:border-zinc-600/50 transition-colors">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${getOpportunityTypeColor(opp.opportunity_type)}`}>
                        {getOpportunityTypeLabel(opp.opportunity_type)}
                      </span>
                      <span className="text-xs text-zinc-500">{formatDate(opp.detected_date)}</span>
                    </div>
                    <p className="text-sm font-medium truncate">{opp.title}</p>
                    <p className="text-xs text-zinc-500 mt-0.5">
                      {opp.keyword} · {opp.region_name || '全球'}
                    </p>
                  </div>
                  <div className="text-right ml-3">
                    <div className="text-lg font-bold text-success">{formatScore(opp.score)}</div>
                    <div className="text-xs text-zinc-500">评分</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-zinc-600 text-sm">
                暂无市场机会数据
                <br />
                <span className="text-xs">等待数据采集和分析...</span>
              </div>
            )}
          </div>
        </div>

        {/* 趋势排行 */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />
              趋势排行榜
            </h2>
            <Link href="/trends" className="text-xs text-zinc-500 hover:text-primary flex items-center gap-1">
              查看全部 <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="space-y-2">
            {analysis && analysis.length > 0 ? (
              analysis.map((item: any, idx: number) => (
                <div key={item.id} className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/50 transition-colors">
                  <span className="text-xs text-zinc-600 w-5 text-center">{idx + 1}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.keyword || 'N/A'}</p>
                    <p className="text-xs text-zinc-500">
                      {item.region_name || '全球'} · 当前 {item.current_score}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-medium ${getTrendColor(item.trend_direction)}`}>
                      {getTrendIcon(item.trend_direction)} {formatScore(Math.abs(item.score_change_pct))}%
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getPotentialColor(item.market_potential)}`}>
                      {getPotentialLabel(item.market_potential)}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-zinc-600 text-sm">
                暂无趋势分析数据
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 采集日志 */}
      {logs && logs.length > 0 && (
        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4">最近采集记录</h2>
          <div className="space-y-2">
            {logs.map((log: any) => (
              <div key={log.id} className="flex items-center justify-between text-sm py-2 border-b border-zinc-800/50 last:border-0">
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${log.status === 'success' ? 'bg-success' : log.status === 'failed' ? 'bg-danger' : 'bg-warning'}`} />
                  <span className="text-zinc-300">{log.task_name}</span>
                  <span className="text-xs text-zinc-500">{log.records_collected} 条记录</span>
                  {log.error_message && (
                    <span className="text-xs text-danger truncate max-w-xs">{log.error_message}</span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-zinc-500">
                  <span>{log.duration_seconds}s</span>
                  <span>{new Date(log.created_at).toLocaleString('zh-CN')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

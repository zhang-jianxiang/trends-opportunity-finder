import { getOpportunityTypeLabel, getOpportunityTypeColor, formatDate, formatScore } from '@/lib/utils'
import { Target, Filter } from 'lucide-react'

async function getOpportunities(type: string): Promise<any[]> {
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/opportunities?type=${type}`,
      { cache: 'no-store' }
    )
    if (!res.ok) throw new Error('Failed to fetch')
    return await res.json()
  } catch {
    return []
  }
}

const filterTypes = [
  { value: 'all', label: '全部' },
  { value: 'trending_up', label: '上升趋势' },
  { value: 'emerging', label: '新兴趋势' },
  { value: 'seasonal', label: '季节性' },
  { value: 'market_gap', label: '市场空白' },
]

export default async function OpportunitiesPage({
  searchParams,
}: {
  searchParams: { type?: string }
}) {
  const type = searchParams.type || 'all'
  const opportunities = await getOpportunities(type)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">市场机会</h1>
        <p className="text-sm text-zinc-500 mt-1">
          基于趋势分析自动识别的市场机会，共 {opportunities.length} 个活跃机会
        </p>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-zinc-500" />
        {filterTypes.map((t) => {
          const isActive = type === t.value
          return (
            <a
              key={t.value}
              href={t.value === 'all' ? '/opportunities' : `/opportunities?type=${t.value}`}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-primary text-white'
                  : 'bg-surface border border-border text-zinc-400 hover:text-white hover:border-zinc-600'
              }`}
            >
              {t.label}
            </a>
          )
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {opportunities.length > 0 ? (
          opportunities.map((opp: any) => (
            <div
              key={opp.id}
              className="bg-surface border border-border rounded-xl p-5 hover:border-zinc-600 transition-colors animate-fade-in"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${getOpportunityTypeColor(opp.opportunity_type)}`}>
                    {getOpportunityTypeLabel(opp.opportunity_type)}
                  </span>
                  <span className="text-xs text-zinc-500">{formatDate(opp.detected_date)}</span>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-success">{formatScore(opp.score)}</div>
                  <div className="text-xs text-zinc-500">机会评分</div>
                </div>
              </div>

              <h3 className="text-base font-semibold mb-2">{opp.title}</h3>
              <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{opp.description}</p>

              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1">
                  <span className="text-zinc-500">关键词:</span>
                  <span className="text-zinc-300">{opp.keyword || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-zinc-500">地区:</span>
                  <span className="text-zinc-300">{opp.region_name || '全球'}</span>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-zinc-800">
                <div className="flex items-center gap-1.5">
                  <span className="text-zinc-500 text-xs">市场规模:</span>
                  <span className="text-zinc-300 text-xs">
                    {opp.market_size === 'massive' ? '极大' :
                     opp.market_size === 'large' ? '大' :
                     opp.market_size === 'medium' ? '中' : '小'}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-zinc-500 text-xs">竞争度:</span>
                  <span className="text-zinc-300 text-xs">
                    {opp.competition_level === 'high' ? '高' :
                     opp.competition_level === 'medium' ? '中' : '低'}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-zinc-500 text-xs">趋势:</span>
                  <span className={`text-xs ${opp.trend_direction === 'up' ? 'text-success' : opp.trend_direction === 'down' ? 'text-danger' : 'text-warning'}`}>
                    {opp.trend_direction === 'up' ? '↗ 上升' : opp.trend_direction === 'down' ? '↘ 下降' : '→ 稳定'}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-16 text-zinc-600">
            <Target className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p className="text-sm">暂无市场机会数据</p>
            <p className="text-xs mt-1">系统每天自动分析并发现新的机会，请耐心等待</p>
          </div>
        )}
      </div>
    </div>
  )
}

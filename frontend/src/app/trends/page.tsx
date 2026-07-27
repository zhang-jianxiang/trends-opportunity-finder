import { supabase } from '@/lib/supabase'
import { getTrendColor, getTrendIcon, getPotentialColor, getPotentialLabel, formatScore } from '@/lib/utils'
import { BarChart3, TrendingUp, AlertTriangle } from 'lucide-react'
import { TrendLineChart, DirectionBarChart } from '@/components/charts'

async function getTrendsData() {
  try {
    // 获取最新分析结果
    const { data: analysis } = await supabase
      .from('trend_analysis')
      .select('*, keywords(keyword, category), regions(region_code, region_name)')
      .order('analysis_date', { ascending: false })
      .order('opportunity_score', { ascending: false })
      .limit(20)

    // 获取异常趋势
    const { data: anomalies } = await supabase
      .from('trend_analysis')
      .select('*, keywords(keyword), regions(region_code, region_name)')
      .eq('is_anomaly', true)
      .order('anomaly_score', { ascending: false })
      .limit(5)

    // 获取趋势历史数据（用于图表）
    const chartData: { name: string; data: { date: string; score: number }[] }[] = []
    
    if (analysis && analysis.length > 0) {
      const topKeywords = analysis.slice(0, 5)
      for (const item of topKeywords) {
        const { data: history } = await supabase
          .from('trends_data')
          .select('date, score')
          .eq('keyword_id', item.keyword_id)
          .eq('region_id', item.region_id)
          .order('date', { ascending: true })
          .limit(30)

        if (history && history.length > 0) {
          const kwName = item.keywords?.keyword || 'N/A'
          const regName = item.regions?.region_code || 'Global'
          chartData.push({
            name: `${kwName} (${regName})`,
            data: history.map((h: { date: string; score: number }) => ({ date: h.date, score: h.score }))
          })
        }
      }
    }

    return { analysis, anomalies, chartData }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
    return { analysis: [], anomalies: [], chartData: [] }
  }
}

export default async function TrendsPage() {
  const { analysis, anomalies, chartData } = await getTrendsData()

  // 准备图表数据
  const allDates = chartData.length > 0
    ? [...new Set(chartData.flatMap(s => s.data.map(d => d.date)))].sort()
    : []

  const mergedChartData = allDates.map(date => {
    const point: Record<string, string | number> = { date }
    for (const series of chartData) {
      const item = series.data.find(d => d.date === date)
      point[series.name] = item ? item.score : 0
    }
    return point
  })

  // 图表系列配置
  const colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
  const seriesConfig = chartData.map((s, idx) => ({
    name: s.name,
    color: colors[idx % colors.length]
  }))

  // 趋势方向分布
  const directionStats = {
    up: analysis?.filter(a => a.trend_direction === 'up').length || 0,
    down: analysis?.filter(a => a.trend_direction === 'down').length || 0,
    stable: analysis?.filter(a => a.trend_direction === 'stable').length || 0,
  }

  const directionChartData = [
    { name: '上升', value: directionStats.up, fill: '#10b981' },
    { name: '下降', value: directionStats.down, fill: '#ef4444' },
    { name: '稳定', value: directionStats.stable, fill: '#f59e0b' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">趋势分析</h1>
        <p className="text-sm text-zinc-500 mt-1">关键词趋势变化和市场热度分析</p>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 趋势折线图 */}
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            Top 5 关键词趋势走势
          </h2>
          <TrendLineChart data={mergedChartData} series={seriesConfig} />
        </div>

        {/* 趋势方向分布 */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-accent" />
            趋势方向分布
          </h2>
          <DirectionBarChart data={directionChartData} />
        </div>
      </div>

      {/* 异常趋势 */}
      {anomalies && anomalies.length > 0 && (
        <div className="bg-surface border border-warning/30 rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-warning" />
            异常趋势警报
            <span className="text-xs text-zinc-500 font-normal">({anomalies.length} 个异常)</span>
          </h2>
          <div className="space-y-2">
            {anomalies.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-lg bg-warning/5 border border-warning/20">
                <div className="flex items-center gap-3">
                  <span className="text-warning text-lg">⚠</span>
                  <div>
                    <p className="text-sm font-medium">{item.keywords?.keyword || 'N/A'}</p>
                    <p className="text-xs text-zinc-500">
                      {item.regions?.region_name || '全球'} · 异常分数: {formatScore(item.anomaly_score)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-warning">+{formatScore(item.score_change_pct)}%</div>
                  <div className="text-xs text-zinc-500">变化率</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 完整趋势表格 */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-lg font-semibold mb-4">所有关键词趋势分析</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-zinc-500 border-b border-border">
                <th className="pb-3 pr-4 font-medium">关键词</th>
                <th className="pb-3 pr-4 font-medium">地区</th>
                <th className="pb-3 pr-4 font-medium text-right">当前分数</th>
                <th className="pb-3 pr-4 font-medium text-right">7日均值</th>
                <th className="pb-3 pr-4 font-medium text-right">变化率</th>
                <th className="pb-3 pr-4 font-medium text-center">趋势</th>
                <th className="pb-3 pr-4 font-medium text-center">潜力</th>
                <th className="pb-3 pr-4 font-medium text-right">机会评分</th>
                <th className="pb-3 font-medium">建议</th>
              </tr>
            </thead>
            <tbody>
              {analysis && analysis.length > 0 ? (
                analysis.map((item) => (
                  <tr key={item.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                    <td className="py-3 pr-4 font-medium">{item.keywords?.keyword || 'N/A'}</td>
                    <td className="py-3 pr-4 text-zinc-400">{item.regions?.region_name || '全球'}</td>
                    <td className="py-3 pr-4 text-right">{item.current_score}</td>
                    <td className="py-3 pr-4 text-right text-zinc-400">{formatScore(item.avg_score_7d)}</td>
                    <td className={`py-3 pr-4 text-right font-medium ${getTrendColor(item.trend_direction)}`}>
                      {getTrendIcon(item.trend_direction)} {formatScore(Math.abs(item.score_change_pct))}%
                    </td>
                    <td className="py-3 pr-4 text-center">
                      <span className={`text-xs ${getTrendColor(item.trend_direction)}`}>
                        {item.trend_direction === 'up' ? '上升' : item.trend_direction === 'down' ? '下降' : '稳定'}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${getPotentialColor(item.market_potential)}`}>
                        {getPotentialLabel(item.market_potential)}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-right font-bold text-primary">{formatScore(item.opportunity_score)}</td>
                    <td className="py-3 text-xs text-zinc-500 max-w-xs truncate">{item.recommendation}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-zinc-600">
                    暂无趋势分析数据，系统每天自动分析更新
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

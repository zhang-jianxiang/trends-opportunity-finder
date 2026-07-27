import { NextResponse } from 'next/server'
import { sql } from '@/lib/db'

// 获取趋势分析数据
export async function GET() {
  try {
    const analysis = await sql`
      SELECT ta.*, k.keyword, k.category, r.region_code, r.region_name
      FROM trend_analysis ta
      JOIN keywords k ON ta.keyword_id = k.id
      JOIN regions r ON ta.region_id = r.id
      ORDER BY ta.analysis_date DESC, ta.opportunity_score DESC LIMIT 20
    `

    const anomalies = await sql`
      SELECT ta.*, k.keyword, r.region_code, r.region_name
      FROM trend_analysis ta
      JOIN keywords k ON ta.keyword_id = k.id
      JOIN regions r ON ta.region_id = r.id
      WHERE ta.is_anomaly = true
      ORDER BY ta.anomaly_score DESC LIMIT 5
    `

    // 获取 Top 5 关键词的历史数据
    const chartData: { name: string; data: { date: string; score: number }[] }[] = []

    for (const item of analysis.slice(0, 5)) {
      const history = await sql`
        SELECT date, score FROM trends_data
        WHERE keyword_id = ${item.keyword_id} AND region_id = ${item.region_id}
        ORDER BY date ASC LIMIT 30
      `
      if (history.length > 0) {
        const kwName = item.keyword || 'N/A'
        const regName = item.region_code || 'Global'
        chartData.push({
          name: `${kwName} (${regName})`,
          data: history.map((h: Record<string, any>) => ({ date: String(h.date), score: Number(h.score) }))
        })
      }
    }

    return NextResponse.json({ analysis, anomalies, chartData })
  } catch (error) {
    console.error('Trends API error:', error)
    return NextResponse.json({ error: 'Failed to fetch trends' }, { status: 500 })
  }
}

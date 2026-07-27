import { NextResponse } from 'next/server'
import { sql } from '@/lib/db'

// 获取仪表板统计数据
export async function GET() {
  try {
    const [keywordRows] = await sql`SELECT COUNT(*) as cnt FROM keywords WHERE is_active = true`
    const [dataRows] = await sql`SELECT COUNT(*) as cnt FROM trends_data`
    const [anomalyRows] = await sql`SELECT COUNT(*) as cnt FROM trend_analysis WHERE is_anomaly = true`

    const opportunities = await sql`
      SELECT o.*, k.keyword, k.category, r.region_code, r.region_name
      FROM opportunities o
      JOIN keywords k ON o.keyword_id = k.id
      JOIN regions r ON o.region_id = r.id
      WHERE o.status = 'active'
      ORDER BY o.score DESC LIMIT 5
    `

    const analysis = await sql`
      SELECT ta.*, k.keyword, k.category, r.region_code, r.region_name
      FROM trend_analysis ta
      JOIN keywords k ON ta.keyword_id = k.id
      JOIN regions r ON ta.region_id = r.id
      ORDER BY ta.analysis_date DESC, ta.opportunity_score DESC LIMIT 8
    `

    const logs = await sql`
      SELECT * FROM collection_logs ORDER BY created_at DESC LIMIT 3
    `

    return NextResponse.json({
      stats: {
        keywordCount: Number(keywordRows.cnt),
        dataCount: Number(dataRows.cnt),
        anomalyCount: Number(anomalyRows.cnt),
        opportunityCount: opportunities.length,
      },
      opportunities,
      analysis,
      logs,
    })
  } catch (error) {
    console.error('Dashboard API error:', error)
    return NextResponse.json({ error: 'Failed to fetch data' }, { status: 500 })
  }
}

import { NextRequest, NextResponse } from 'next/server'
import { sql } from '@/lib/db'

// 获取市场机会列表
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') || 'all'

    let opportunities
    if (type === 'all') {
      opportunities = await sql`
        SELECT o.*, k.keyword, k.category, r.region_code, r.region_name
        FROM opportunities o
        JOIN keywords k ON o.keyword_id = k.id
        JOIN regions r ON o.region_id = r.id
        WHERE o.status = 'active'
        ORDER BY o.score DESC LIMIT 50
      `
    } else {
      opportunities = await sql`
        SELECT o.*, k.keyword, k.category, r.region_code, r.region_name
        FROM opportunities o
        JOIN keywords k ON o.keyword_id = k.id
        JOIN regions r ON o.region_id = r.id
        WHERE o.status = 'active' AND o.opportunity_type = ${type}
        ORDER BY o.score DESC LIMIT 50
      `
    }

    return NextResponse.json(opportunities)
  } catch (error) {
    console.error('Opportunities API error:', error)
    return NextResponse.json({ error: 'Failed to fetch opportunities' }, { status: 500 })
  }
}

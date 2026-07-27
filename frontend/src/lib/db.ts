import { neon } from '@neondatabase/serverless'

// Neon 连接字符串（在 Vercel 环境变量中配置 DATABASE_URL）
const databaseUrl = process.env.DATABASE_URL || ''

if (!databaseUrl) {
  console.warn('DATABASE_URL 未配置，请在 .env.local 中设置')
}

// 创建 SQL 查询函数
export const sql = neon(databaseUrl || 'postgresql://placeholder:placeholder@ep-placeholder.neon.tech/db')

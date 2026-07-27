import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'
import { TrendingUp, LayoutDashboard, Target, BarChart3 } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Google Trends 市场机会分析',
  description: '自动采集 Google Trends 数据，分析市场趋势，发掘商业机会',
}

const navItems = [
  { href: '/', label: '仪表板', icon: LayoutDashboard },
  { href: '/opportunities', label: '市场机会', icon: Target },
  { href: '/trends', label: '趋势分析', icon: BarChart3 },
]

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          {/* 侧边栏 */}
          <aside className="w-60 border-r border-border bg-surface flex-shrink-0 hidden md:flex md:flex-col">
            <div className="p-5 border-b border-border">
              <Link href="/" className="flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-primary" />
                <span className="text-lg font-bold gradient-text">Trends 分析</span>
              </Link>
            </div>
            <nav className="flex-1 p-3 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-colors"
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="p-4 border-t border-border">
              <p className="text-xs text-zinc-600">
                数据由 GitHub Actions
                <br />
                每日自动采集更新
              </p>
            </div>
          </aside>

          {/* 主内容区 */}
          <main className="flex-1 overflow-x-hidden">
            {/* 移动端导航 */}
            <div className="md:hidden flex items-center gap-4 px-4 py-3 border-b border-border bg-surface overflow-x-auto">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-zinc-400 hover:text-white hover:bg-zinc-800/50 whitespace-nowrap"
                >
                  <item.icon className="w-3.5 h-3.5" />
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="p-6 max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}

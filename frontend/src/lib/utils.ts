import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

export function formatScore(score: number): string {
  return score.toFixed(1)
}

export function getTrendColor(direction: string): string {
  switch (direction) {
    case 'up': return 'text-success'
    case 'down': return 'text-danger'
    default: return 'text-warning'
  }
}

export function getTrendIcon(direction: string): string {
  switch (direction) {
    case 'up': return '↗'
    case 'down': return '↘'
    default: return '→'
  }
}

export function getPotentialColor(potential: string): string {
  switch (potential) {
    case 'high': return 'bg-success/20 text-success border-success/30'
    case 'medium': return 'bg-warning/20 text-warning border-warning/30'
    default: return 'bg-zinc-700/40 text-zinc-400 border-zinc-600/30'
  }
}

export function getPotentialLabel(potential: string): string {
  switch (potential) {
    case 'high': return '高'
    case 'medium': return '中'
    default: return '低'
  }
}

export function getOpportunityTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    trending_up: '上升趋势',
    emerging: '新兴趋势',
    seasonal: '季节性',
    market_gap: '市场空白',
  }
  return labels[type] || type
}

export function getOpportunityTypeColor(type: string): string {
  const colors: Record<string, string> = {
    trending_up: 'bg-success/20 text-success border-success/30',
    emerging: 'bg-accent/20 text-accent border-accent/30',
    seasonal: 'bg-warning/20 text-warning border-warning/30',
    market_gap: 'bg-primary/20 text-primary border-primary/30',
  }
  return colors[type] || 'bg-zinc-700/40 text-zinc-400 border-zinc-600/30'
}

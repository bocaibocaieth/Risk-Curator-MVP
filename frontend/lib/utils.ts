import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number | undefined, decimals = 2): string {
  if (value === undefined || value === null) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercent(value: number | undefined): string {
  if (value === undefined || value === null) return '-'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function scoreToGrade(score: number): string {
  const mapping: Record<number, string> = {
    1: 'AA',
    2: 'A',
    3: 'BB',
    4: 'B',
    5: 'CC',
    6: 'C',
  }
  return mapping[score] || 'C'
}

export function gradeToScore(grade: string): number {
  const mapping: Record<string, number> = {
    'AA': 1,
    'A': 2,
    'BB': 3,
    'B': 4,
    'CC': 5,
    'C': 6,
  }
  return mapping[grade.toUpperCase()] || 6
}

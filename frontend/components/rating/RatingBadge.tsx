'use client'

import { cn } from '@/lib/utils'
import { RATING_COLORS, VAULT_ELIGIBILITY_COLORS, type RatingGrade, type VaultEligibility } from '@/types'

interface RatingBadgeProps {
  rating: string
  size?: 'sm' | 'md' | 'lg'
}

export function RatingBadge({ rating, size = 'md' }: RatingBadgeProps) {
  const colorClass = RATING_COLORS[rating as RatingGrade] || 'bg-gray-500 text-white'
  const sizeClass = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }[size]

  return (
    <span className={cn('rounded font-bold', colorClass, sizeClass)}>
      {rating}
    </span>
  )
}

interface VaultEligibilityBadgeProps {
  eligibility: VaultEligibility
}

export function VaultEligibilityBadge({ eligibility }: VaultEligibilityBadgeProps) {
  const colorClass = VAULT_ELIGIBILITY_COLORS[eligibility] || 'bg-gray-100 text-gray-800'

  return (
    <span className={cn('rounded-full border px-2.5 py-0.5 text-xs font-medium', colorClass)}>
      {eligibility}
    </span>
  )
}

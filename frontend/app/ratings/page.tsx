'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Plus, Star } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RatingBadge, VaultEligibilityBadge } from '@/components/rating/RatingBadge'
import { ratingsApi } from '@/lib/api'
import { formatDate, scoreToGrade } from '@/lib/utils'
import type { VaultEligibility } from '@/types'

export default function RatingsPage() {
  const { data: ratings, isLoading } = useQuery({
    queryKey: ['ratings'],
    queryFn: () => ratingsApi.list({ size: 100 }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Ratings</h1>
          <p className="text-muted-foreground">Asset risk ratings</p>
        </div>
        <Link href="/ratings/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Rating
          </Button>
        </Link>
      </div>

      {/* Ratings Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <p>Loading...</p>
          ) : ratings?.items.length === 0 ? (
            <div className="text-center py-8">
              <Star className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-2 text-lg font-medium">No ratings yet</h3>
              <p className="text-muted-foreground">Create your first asset rating</p>
              <Link href="/ratings/new">
                <Button className="mt-4">
                  <Plus className="mr-2 h-4 w-4" />
                  New Rating
                </Button>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                    <th className="pb-3 pr-4">Asset</th>
                    <th className="pb-3 pr-4">Issuer Risk</th>
                    <th className="pb-3 pr-4">Credit Risk</th>
                    <th className="pb-3 pr-4">Operational</th>
                    <th className="pb-3 pr-4">Final Rating</th>
                    <th className="pb-3 pr-4">Vault</th>
                    <th className="pb-3 pr-4">Rated By</th>
                    <th className="pb-3">Rated At</th>
                  </tr>
                </thead>
                <tbody>
                  {ratings?.items.map((rating) => (
                    <tr key={rating.id} className="border-b">
                      <td className="py-3 pr-4">
                        <div>
                          <span className="font-medium">{rating.asset_symbol}</span>
                          <p className="text-sm text-muted-foreground">
                            {rating.asset_name}
                          </p>
                        </div>
                      </td>
                      <td className="py-3 pr-4">
                        <RatingBadge rating={rating.issuer_risk_rating} size="sm" />
                      </td>
                      <td className="py-3 pr-4">
                        <RatingBadge
                          rating={scoreToGrade(rating.credit_risk_score)}
                          size="sm"
                        />
                      </td>
                      <td className="py-3 pr-4">
                        <RatingBadge rating={rating.operational_risk_rating} size="sm" />
                      </td>
                      <td className="py-3 pr-4">
                        <RatingBadge rating={rating.asset_rating} size="md" />
                      </td>
                      <td className="py-3 pr-4">
                        <VaultEligibilityBadge
                          eligibility={rating.vault_eligibility as VaultEligibility}
                        />
                      </td>
                      <td className="py-3 pr-4 text-sm text-muted-foreground">
                        {rating.rated_by}
                      </td>
                      <td className="py-3 text-sm text-muted-foreground">
                        {formatDate(rating.rated_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

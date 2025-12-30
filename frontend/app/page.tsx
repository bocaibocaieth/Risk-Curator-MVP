'use client'

import { useQuery } from '@tanstack/react-query'
import { Coins, DollarSign, Bell, Star, CheckCircle, AlertTriangle } from 'lucide-react'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RatingBadge, VaultEligibilityBadge } from '@/components/rating/RatingBadge'
import { assetsApi, ratingsApi, alertsApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { VaultEligibility } from '@/types'

export default function DashboardPage() {
  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list({ size: 100 }),
  })

  const { data: ratings } = useQuery({
    queryKey: ['ratings'],
    queryFn: () => ratingsApi.list({ size: 100 }),
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.listHistory({ size: 10, acknowledged: false }),
  })

  const { data: alertConfigs } = useQuery({
    queryKey: ['alertConfigs'],
    queryFn: () => alertsApi.listConfigs({ is_active: true }),
  })

  // Calculate rating distribution
  const ratingDistribution = ratings?.items.reduce(
    (acc, r) => {
      const eligibility = r.vault_eligibility as VaultEligibility
      acc[eligibility] = (acc[eligibility] || 0) + 1
      return acc
    },
    {} as Record<VaultEligibility, number>
  ) || {}

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">DeFi Risk Monitoring Overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Monitored Assets"
          value={assets?.total || 0}
          description="Active assets being tracked"
          icon={Coins}
        />
        <StatsCard
          title="Rated Assets"
          value={ratings?.total || 0}
          description="Assets with ratings"
          icon={Star}
        />
        <StatsCard
          title="Active Alerts"
          value={alertConfigs?.total || 0}
          description="Alert configurations"
          icon={Bell}
        />
        <StatsCard
          title="Unacknowledged"
          value={alerts?.total || 0}
          description="Pending alert notifications"
          icon={AlertTriangle}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Rating Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Vault Eligibility Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(['Prime', 'High Yield', 'Constrained', 'Excluded'] as VaultEligibility[]).map(
                (eligibility) => (
                  <div key={eligibility} className="flex items-center justify-between">
                    <VaultEligibilityBadge eligibility={eligibility} />
                    <span className="text-2xl font-bold">
                      {ratingDistribution[eligibility] || 0}
                    </span>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            {alerts?.items.length === 0 ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>No pending alerts</span>
              </div>
            ) : (
              <div className="space-y-3">
                {alerts?.items.slice(0, 5).map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-start justify-between rounded-lg border p-3"
                  >
                    <div>
                      <p className="font-medium">{alert.alert_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(alert.triggered_at)}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${
                        alert.severity === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : alert.severity === 'high'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Asset Table */}
      <Card>
        <CardHeader>
          <CardTitle>Monitored Assets</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                  <th className="pb-3 pr-4">Symbol</th>
                  <th className="pb-3 pr-4">Name</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Chain</th>
                  <th className="pb-3 pr-4">Rating</th>
                  <th className="pb-3">Vault Eligibility</th>
                </tr>
              </thead>
              <tbody>
                {assets?.items.slice(0, 10).map((asset) => (
                  <tr key={asset.id} className="border-b">
                    <td className="py-3 pr-4 font-medium">{asset.symbol}</td>
                    <td className="py-3 pr-4 text-muted-foreground">{asset.name}</td>
                    <td className="py-3 pr-4">
                      <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                        {asset.asset_type || '-'}
                      </span>
                    </td>
                    <td className="py-3 pr-4">{asset.chain}</td>
                    <td className="py-3 pr-4">
                      {asset.asset_rating ? (
                        <RatingBadge rating={asset.asset_rating} size="sm" />
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="py-3">
                      {asset.vault_eligibility ? (
                        <VaultEligibilityBadge
                          eligibility={asset.vault_eligibility as VaultEligibility}
                        />
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

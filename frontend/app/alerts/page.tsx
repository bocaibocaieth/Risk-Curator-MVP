'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Bell, Trash2, Play, History } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { alertsApi, assetsApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { AlertConfigCreate, AlertType } from '@/types'

export default function AlertsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)

  const { data: configs, isLoading } = useQuery({
    queryKey: ['alertConfigs'],
    queryFn: () => alertsApi.listConfigs(),
  })

  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list({ size: 100 }),
  })

  const createMutation = useMutation({
    mutationFn: alertsApi.createConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertConfigs'] })
      setShowForm(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: alertsApi.deleteConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertConfigs'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      alertsApi.updateConfig(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertConfigs'] })
    },
  })

  const testMutation = useMutation({
    mutationFn: (id: number) => alertsApi.testConfig(id),
    onSuccess: () => {
      alert('Test alert sent!')
    },
    onError: () => {
      alert('Failed to send test alert')
    },
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data: AlertConfigCreate = {
      name: formData.get('name') as string,
      alert_type: formData.get('alert_type') as AlertType,
      asset_id: formData.get('asset_id') ? parseInt(formData.get('asset_id') as string) : undefined,
      threshold_percent: parseFloat(formData.get('threshold_percent') as string),
      telegram_chat_id: formData.get('telegram_chat_id') as string,
      cooldown_minutes: parseInt(formData.get('cooldown_minutes') as string) || 60,
    }
    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Alerts</h1>
          <p className="text-muted-foreground">Configure alert notifications</p>
        </div>
        <div className="flex gap-2">
          <Link href="/alerts/history">
            <Button variant="outline">
              <History className="mr-2 h-4 w-4" />
              History
            </Button>
          </Link>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-2 h-4 w-4" />
            New Alert
          </Button>
        </div>
      </div>

      {/* Create Alert Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create Alert Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  name="name"
                  required
                  placeholder="e.g., USDC Depeg Alert"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Alert Type *</label>
                <select name="alert_type" required className="w-full rounded-md border px-3 py-2">
                  <option value="depeg">Depeg (Stablecoins)</option>
                  <option value="price_deviation">Price Deviation</option>
                  <option value="tvl_drop">TVL Drop</option>
                  <option value="liquidity">Liquidity Alert</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Asset</label>
                <select name="asset_id" className="w-full rounded-md border px-3 py-2">
                  <option value="">All assets</option>
                  {assets?.items.map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.symbol} - {asset.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Threshold % *</label>
                <input
                  name="threshold_percent"
                  type="number"
                  step="0.01"
                  required
                  placeholder="e.g., 1.0"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Telegram Chat ID *</label>
                <input
                  name="telegram_chat_id"
                  required
                  placeholder="e.g., -1001234567890"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Cooldown (minutes)</label>
                <input
                  name="cooldown_minutes"
                  type="number"
                  defaultValue={60}
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div className="md:col-span-2 flex gap-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Alert'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Alert Configs Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <p>Loading...</p>
          ) : configs?.items.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-2 text-lg font-medium">No alerts configured</h3>
              <p className="text-muted-foreground">Create your first alert</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                    <th className="pb-3 pr-4">Name</th>
                    <th className="pb-3 pr-4">Type</th>
                    <th className="pb-3 pr-4">Asset</th>
                    <th className="pb-3 pr-4">Threshold</th>
                    <th className="pb-3 pr-4">Status</th>
                    <th className="pb-3 pr-4">Last Triggered</th>
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {configs?.items.map((config) => (
                    <tr key={config.id} className="border-b">
                      <td className="py-3 pr-4 font-medium">{config.name}</td>
                      <td className="py-3 pr-4">
                        <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                          {config.alert_type}
                        </span>
                      </td>
                      <td className="py-3 pr-4">{config.asset_symbol || 'All'}</td>
                      <td className="py-3 pr-4">{config.threshold_percent}%</td>
                      <td className="py-3 pr-4">
                        <button
                          onClick={() =>
                            toggleMutation.mutate({
                              id: config.id,
                              is_active: !config.is_active,
                            })
                          }
                          className={`rounded-full px-2 py-1 text-xs font-medium ${
                            config.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {config.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="py-3 pr-4 text-sm text-muted-foreground">
                        {config.last_triggered_at
                          ? formatDate(config.last_triggered_at)
                          : 'Never'}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => testMutation.mutate(config.id)}
                            disabled={testMutation.isPending}
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => {
                              if (confirm('Delete this alert?')) {
                                deleteMutation.mutate(config.id)
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
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

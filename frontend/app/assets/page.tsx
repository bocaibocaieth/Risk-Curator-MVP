'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RatingBadge, VaultEligibilityBadge } from '@/components/rating/RatingBadge'
import { assetsApi } from '@/lib/api'
import type { Asset, VaultEligibility } from '@/types'

export default function AssetsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const { data: assets, isLoading } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list({ size: 100 }),
  })

  const createMutation = useMutation({
    mutationFn: assetsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      setShowForm(false)
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message || 'Failed to create asset')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: assetsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      setDeletingId(null)
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message || 'Failed to delete asset')
      setDeletingId(null)
    },
  })

  // Validate Ethereum contract address format
  const isValidContractAddress = (address: string): boolean => {
    if (!address) return true // Empty is allowed
    return /^0x[0-9a-fA-F]{40}$/.test(address)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const contractAddress = (formData.get('contract_address') as string) || ''

    // Validate contract address format
    if (contractAddress && !isValidContractAddress(contractAddress)) {
      setError('Invalid contract address format. Must be a valid Ethereum address (0x...)')
      return
    }

    const data = {
      symbol: formData.get('symbol') as string,
      name: formData.get('name') as string,
      asset_type: formData.get('asset_type') as string || null,
      chain: formData.get('chain') as string || 'ethereum',
      coingecko_id: formData.get('coingecko_id') as string || null,
      contract_address: contractAddress || null,
    }
    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Assets</h1>
          <p className="text-muted-foreground">Manage monitored assets</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Asset
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-50 p-4 text-red-700 border border-red-200">
          <p className="text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs underline hover:no-underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Add Asset Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add New Asset</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium mb-1">Symbol *</label>
                <input
                  name="symbol"
                  required
                  maxLength={20}
                  placeholder="e.g., USDC"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  name="name"
                  required
                  placeholder="e.g., USD Coin"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select name="asset_type" className="w-full rounded-md border px-3 py-2">
                  <option value="">Select type</option>
                  <option value="stablecoin">Stablecoin</option>
                  <option value="lst">LST (Liquid Staking)</option>
                  <option value="lrt">LRT (Liquid Restaking)</option>
                  <option value="pt">PT (Principal Token)</option>
                  <option value="native">Native</option>
                  <option value="rwa">RWA</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Chain</label>
                <select name="chain" className="w-full rounded-md border px-3 py-2">
                  <option value="ethereum">Ethereum</option>
                  <option value="arbitrum">Arbitrum</option>
                  <option value="base">Base</option>
                  <option value="polygon">Polygon</option>
                  <option value="optimism">Optimism</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">CoinGecko ID</label>
                <input
                  name="coingecko_id"
                  placeholder="e.g., usd-coin"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Contract Address</label>
                <input
                  name="contract_address"
                  placeholder="0x..."
                  pattern="^0x[0-9a-fA-F]{40}$"
                  title="Must be a valid Ethereum address (0x followed by 40 hex characters)"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div className="md:col-span-2 flex gap-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Asset'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Assets Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <p>Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                    <th className="pb-3 pr-4">Symbol</th>
                    <th className="pb-3 pr-4">Name</th>
                    <th className="pb-3 pr-4">Type</th>
                    <th className="pb-3 pr-4">Chain</th>
                    <th className="pb-3 pr-4">CoinGecko ID</th>
                    <th className="pb-3 pr-4">Rating</th>
                    <th className="pb-3 pr-4">Vault</th>
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {assets?.items.map((asset) => (
                    <tr key={asset.id} className="border-b">
                      <td className="py-3 pr-4 font-medium">{asset.symbol}</td>
                      <td className="py-3 pr-4 text-muted-foreground">{asset.name}</td>
                      <td className="py-3 pr-4">
                        <span className="rounded bg-gray-100 px-2 py-1 text-xs">
                          {asset.asset_type || '-'}
                        </span>
                      </td>
                      <td className="py-3 pr-4">{asset.chain}</td>
                      <td className="py-3 pr-4 text-sm text-muted-foreground">
                        {asset.coingecko_id || '-'}
                      </td>
                      <td className="py-3 pr-4">
                        {asset.asset_rating ? (
                          <RatingBadge rating={asset.asset_rating} size="sm" />
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="py-3 pr-4">
                        {asset.vault_eligibility ? (
                          <VaultEligibilityBadge
                            eligibility={asset.vault_eligibility as VaultEligibility}
                          />
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="py-3">
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={deletingId === asset.id}
                          onClick={() => {
                            if (confirm('Delete this asset?')) {
                              setDeletingId(asset.id)
                              deleteMutation.mutate(asset.id)
                            }
                          }}
                        >
                          {deletingId === asset.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4 text-red-500" />
                          )}
                        </Button>
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

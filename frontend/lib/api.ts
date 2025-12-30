import axios from 'axios'
import type {
  Asset,
  AssetListResponse,
  AssetRating,
  RatingListResponse,
  AssetRatingCreate,
  AlertConfig,
  AlertConfigCreate,
  AlertHistoryListResponse,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Assets API
export const assetsApi = {
  list: async (params?: {
    page?: number
    size?: number
    asset_type?: string
    chain?: string
    is_active?: boolean
    search?: string
  }): Promise<AssetListResponse> => {
    const { data } = await api.get('/assets', { params })
    return data
  },

  get: async (id: number): Promise<Asset> => {
    const { data } = await api.get(`/assets/${id}`)
    return data
  },

  create: async (asset: Partial<Asset>): Promise<Asset> => {
    const { data } = await api.post('/assets', asset)
    return data
  },

  update: async (id: number, asset: Partial<Asset>): Promise<Asset> => {
    const { data } = await api.put(`/assets/${id}`, asset)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/assets/${id}`)
  },
}

// Ratings API
export const ratingsApi = {
  list: async (params?: {
    page?: number
    size?: number
    asset_rating?: string
    vault_eligibility?: string
  }): Promise<RatingListResponse> => {
    const { data } = await api.get('/ratings/assets', { params })
    return data
  },

  get: async (assetId: number): Promise<AssetRating> => {
    const { data } = await api.get(`/ratings/assets/${assetId}`)
    return data
  },

  create: async (rating: AssetRatingCreate): Promise<AssetRating> => {
    const { data } = await api.post('/ratings/assets', rating)
    return data
  },

  update: async (assetId: number, rating: Partial<AssetRatingCreate>): Promise<AssetRating> => {
    const { data } = await api.put(`/ratings/assets/${assetId}`, rating)
    return data
  },

  delete: async (assetId: number): Promise<void> => {
    await api.delete(`/ratings/assets/${assetId}`)
  },
}

// Alerts API
export const alertsApi = {
  listConfigs: async (params?: {
    is_active?: boolean
    alert_type?: string
  }): Promise<{ items: AlertConfig[]; total: number }> => {
    const { data } = await api.get('/alerts/configs', { params })
    return data
  },

  getConfig: async (id: number): Promise<AlertConfig> => {
    const { data } = await api.get(`/alerts/configs/${id}`)
    return data
  },

  createConfig: async (config: AlertConfigCreate): Promise<AlertConfig> => {
    const { data } = await api.post('/alerts/configs', config)
    return data
  },

  updateConfig: async (id: number, config: Partial<AlertConfigCreate & { is_active?: boolean }>): Promise<AlertConfig> => {
    const { data } = await api.put(`/alerts/configs/${id}`, config)
    return data
  },

  deleteConfig: async (id: number): Promise<void> => {
    await api.delete(`/alerts/configs/${id}`)
  },

  testConfig: async (id: number, message?: string): Promise<{ status: string; message: string }> => {
    const { data } = await api.post(`/alerts/configs/${id}/test`, { message })
    return data
  },

  listHistory: async (params?: {
    page?: number
    size?: number
    config_id?: number
    severity?: string
    acknowledged?: boolean
  }): Promise<AlertHistoryListResponse> => {
    const { data } = await api.get('/alerts/history', { params })
    return data
  },

  acknowledgeAlert: async (historyId: number): Promise<void> => {
    await api.put(`/alerts/history/${historyId}/acknowledge`)
  },
}

// Monitor API
export const monitorApi = {
  getPrice: async (assetId: number): Promise<{
    asset_id: number
    symbol: string
    price_usd: number | null
    source: string | null
    error: string | null
  }> => {
    const { data } = await api.get(`/monitor/prices/${assetId}`)
    return data
  },

  getPrices: async (assetIds: number[]): Promise<{
    prices: Array<{
      asset_id: number
      symbol: string
      price_usd: number | null
      source: string | null
      error: string | null
    }>
  }> => {
    const { data } = await api.get('/monitor/prices', {
      params: { asset_ids: assetIds.join(',') },
    })
    return data
  },

  getTvl: async (protocolSlug: string): Promise<{
    protocol: string
    tvl_usd: number | null
    change_24h: number | null
    error: string | null
  }> => {
    const { data } = await api.get(`/monitor/tvl/${protocolSlug}`)
    return data
  },

  triggerCheck: async (): Promise<{
    checked_assets: number
    alerts_triggered: number
    messages: string[]
  }> => {
    const { data } = await api.post('/monitor/check')
    return data
  },
}

export default api

import axios, { AxiosError, AxiosRequestConfig } from 'axios'
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
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ''

// Retry configuration
const MAX_RETRIES = 3
const RETRY_DELAY_MS = 1000

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public errorCode?: string,
    public details?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Sleep helper for retry delay
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Check if error is retryable
const isRetryable = (error: AxiosError): boolean => {
  // Retry on network errors or 5xx server errors
  if (!error.response) return true // Network error
  const status = error.response.status
  return status >= 500 || status === 429 // Server error or rate limit
}

// Create axios instance with timeout
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    // Add timestamp for debugging
    config.metadata = { startTime: new Date() }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { _retryCount?: number }

    // Initialize retry count
    if (!config._retryCount) {
      config._retryCount = 0
    }

    // Check if we should retry
    if (isRetryable(error) && config._retryCount < MAX_RETRIES) {
      config._retryCount++
      const delay = RETRY_DELAY_MS * Math.pow(2, config._retryCount - 1) // Exponential backoff
      console.warn(`Retrying request (${config._retryCount}/${MAX_RETRIES}) after ${delay}ms`)
      await sleep(delay)
      return api(config)
    }

    // Transform error to ApiError
    if (error.response) {
      const data = error.response.data as { message?: string; error?: string; details?: Record<string, unknown> }
      throw new ApiError(
        data?.message || error.message || 'An error occurred',
        error.response.status,
        data?.error,
        data?.details
      )
    } else if (error.request) {
      throw new ApiError('Network error - please check your connection', 0, 'NETWORK_ERROR')
    } else {
      throw new ApiError(error.message || 'Request failed', 0, 'REQUEST_ERROR')
    }
  }
)

// Extend axios config type for metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: { startTime: Date }
    _retryCount?: number
  }
}

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

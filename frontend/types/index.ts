// Asset Types
export interface Asset {
  id: number;
  symbol: string;
  name: string;
  asset_type: 'stablecoin' | 'lst' | 'lrt' | 'pt' | 'native' | 'rwa' | null;
  chain: string;
  contract_address?: string;
  coingecko_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  current_price?: number;
  price_change_24h?: number;
  asset_rating?: string;
  vault_eligibility?: string;
}

export interface AssetListResponse {
  items: Asset[];
  total: number;
  page: number;
  size: number;
}

// Rating Types
export interface AssetRating {
  id: number;
  asset_id: number;
  asset_symbol?: string;
  asset_name?: string;

  // Raw scores (1-6)
  issuer_social_score: number;
  issuer_decentralization_score: number;
  issuer_technical_score: number;
  credit_risk_score: number;
  operational_lindy_score: number;
  operational_audit_score: number;
  operational_transparency_score: number;

  // Computed ratings
  issuer_risk_rating: string;
  operational_risk_rating: string;
  asset_rating: string;
  vault_eligibility: VaultEligibility;

  rated_by: string;
  rating_notes?: string;
  rated_at: string;
}

export interface RatingListResponse {
  items: AssetRating[];
  total: number;
  page: number;
  size: number;
}

// Alert Types
export interface AlertConfig {
  id: number;
  name: string;
  alert_type: AlertType;
  asset_id?: number;
  asset_symbol?: string;
  protocol_id?: number;
  protocol_name?: string;
  threshold_percent: number;
  telegram_chat_id: string;
  cooldown_minutes: number;
  is_active: boolean;
  last_triggered_at?: string;
  created_at: string;
}

export interface AlertHistory {
  id: number;
  alert_config_id: number;
  alert_name?: string;
  triggered_value?: number;
  message?: string;
  severity: Severity;
  acknowledged: boolean;
  triggered_at: string;
}

export interface AlertHistoryListResponse {
  items: AlertHistory[];
  total: number;
  page: number;
  size: number;
}

// Enums and Constants
export type AlertType = 'price_deviation' | 'depeg' | 'tvl_drop' | 'liquidity';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type VaultEligibility = 'Prime' | 'High Yield' | 'Constrained' | 'Excluded';

export const RATING_GRADES = ['AA', 'A', 'BB', 'B', 'CC', 'C'] as const;
export type RatingGrade = typeof RATING_GRADES[number];

export const RATING_COLORS: Record<RatingGrade, string> = {
  'AA': 'bg-green-500 text-white',
  'A': 'bg-green-400 text-white',
  'BB': 'bg-yellow-500 text-white',
  'B': 'bg-yellow-400 text-black',
  'CC': 'bg-orange-500 text-white',
  'C': 'bg-red-500 text-white',
};

export const VAULT_ELIGIBILITY_COLORS: Record<VaultEligibility, string> = {
  'Prime': 'bg-green-100 text-green-800 border-green-200',
  'High Yield': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'Constrained': 'bg-orange-100 text-orange-800 border-orange-200',
  'Excluded': 'bg-red-100 text-red-800 border-red-200',
};

export const SEVERITY_COLORS: Record<Severity, string> = {
  'low': 'bg-blue-100 text-blue-800',
  'medium': 'bg-yellow-100 text-yellow-800',
  'high': 'bg-orange-100 text-orange-800',
  'critical': 'bg-red-100 text-red-800',
};

// Form Types
export interface IssuerRiskInput {
  social_score: number;
  decentralization_score: number;
  technical_score: number;
}

export interface CreditRiskInput {
  credit_risk_score: number;
}

export interface OperationalRiskInput {
  lindy_score: number;
  audit_score: number;
  transparency_score: number;
}

export interface AssetRatingCreate {
  asset_id: number;
  issuer: IssuerRiskInput;
  credit: CreditRiskInput;
  operational: OperationalRiskInput;
  rating_notes?: string;
  rated_by: string;
}

export interface AlertConfigCreate {
  name: string;
  alert_type: AlertType;
  asset_id?: number;
  protocol_id?: number;
  threshold_percent: number;
  telegram_chat_id: string;
  cooldown_minutes: number;
}

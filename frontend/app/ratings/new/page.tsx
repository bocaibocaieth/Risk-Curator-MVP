'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { ArrowLeft, ArrowRight, Check, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { RatingBadge, VaultEligibilityBadge } from '@/components/rating/RatingBadge'
import { assetsApi, ratingsApi } from '@/lib/api'
import { scoreToGrade } from '@/lib/utils'
import type { AssetRatingCreate, VaultEligibility } from '@/types'

const SCORE_DESCRIPTIONS = {
  social: [
    '1 (AA): 受监管实体，完整牌照，知名机构',
    '2 (A): 已识别团队，部分监管，良好声誉',
    '3 (BB): 团队公开，无监管但透明',
    '4 (B): 团队部分公开，有限透明度',
    '5 (CC): 匿名团队，仅多签身份',
    '6 (C): 完全匿名，无法追踪',
  ],
  decentralization: [
    '1 (AA): 完全去中心化DAO，广泛代币分布',
    '2 (A): DAO治理，合理分布，定期投票',
    '3 (BB): 有治理机制，但集中度较高',
    '4 (B): 有限治理，少数人控制',
    '5 (CC): 名义上的DAO，实际中心化',
    '6 (C): 完全中心化，无治理',
  ],
  technical: [
    '1 (AA): 核心合约不可变，无管理员权限',
    '2 (A): 不可变合约，仅有限参数可调',
    '3 (BB): 可升级但有时间锁(7天+)',
    '4 (B): 可升级，短时间锁(1-7天)',
    '5 (CC): 可升级，无时间锁',
    '6 (C): 完全可控，可随时修改',
  ],
  credit: [
    '1 (AA): 最高质量，如USDC/USDT',
    '2 (A): 高质量，如DAI',
    '3 (BB): 中等，如LST (stETH)',
    '4 (B): 较高风险，如LRT或新稳定币',
    '5 (CC): 高风险，如算法稳定币',
    '6 (C): 极高风险，有问题历史',
  ],
  lindy: [
    '1 (AA): 3年+运营，$1B+ TVL，零事故',
    '2 (A): 2年+运营，$500M+ TVL',
    '3 (BB): 1年+运营，$100M+ TVL',
    '4 (B): 6个月+运营，$50M+ TVL',
    '5 (CC): 3个月+运营，或TVL较低',
    '6 (C): 新协议，未经验证',
  ],
  audit: [
    '1 (AA): 3+顶级审计，$1M+ Bug Bounty',
    '2 (A): 2+知名审计，有Bug Bounty',
    '3 (BB): 1+审计，已修复所有问题',
    '4 (B): 有审计但有未解决问题',
    '5 (CC): 仅一次审计或不知名审计公司',
    '6 (C): 无审计',
  ],
  transparency: [
    '1 (AA): 完全链上可验证，实时储备证明',
    '2 (A): 链上数据+定期报告',
    '3 (BB): 定期第三方审计报告',
    '4 (B): 仅有团队自行报告',
    '5 (CC): 有限透明度',
    '6 (C): 不透明',
  ],
}

interface ScoreSliderProps {
  label: string
  value: number
  onChange: (value: number) => void
  descriptions: string[]
}

function ScoreSlider({ label, value, onChange, descriptions }: ScoreSliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">{label}</label>
        <RatingBadge rating={scoreToGrade(value)} size="sm" />
      </div>
      <input
        type="range"
        min={1}
        max={6}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>AA (Best)</span>
        <span>C (Worst)</span>
      </div>
      <div className="mt-2 rounded-lg bg-gray-50 p-2">
        <p className="text-xs text-muted-foreground">{descriptions[value - 1]}</p>
      </div>
    </div>
  )
}

export default function NewRatingPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [scores, setScores] = useState({
    social: 3,
    decentralization: 3,
    technical: 3,
    credit: 3,
    lindy: 3,
    audit: 3,
    transparency: 3,
  })
  const [ratedBy, setRatedBy] = useState('')
  const [notes, setNotes] = useState('')

  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list({ size: 100 }),
  })

  const createMutation = useMutation({
    mutationFn: ratingsApi.create,
    onSuccess: () => {
      router.push('/ratings')
    },
    onError: (err: Error) => {
      setError(err.message || 'Failed to create rating')
    },
  })

  const selectedAsset = assets?.items.find((a) => a.id === selectedAssetId)

  // Calculate ratings
  const issuerRisk = scoreToGrade(Math.min(scores.social, scores.decentralization, scores.technical))
  const operationalRisk = scoreToGrade(Math.max(scores.lindy, scores.audit, scores.transparency))
  const finalRating = scoreToGrade(
    Math.max(
      Math.min(scores.social, scores.decentralization, scores.technical),
      scores.credit,
      Math.max(scores.lindy, scores.audit, scores.transparency)
    )
  )

  const getVaultEligibility = (rating: string): VaultEligibility => {
    const score = { AA: 1, A: 2, BB: 3, B: 4, CC: 5, C: 6 }[rating] || 6
    if (score <= 2) return 'Prime'
    if (score <= 4) return 'High Yield'
    if (score === 5) return 'Constrained'
    return 'Excluded'
  }

  const handleSubmit = () => {
    if (!selectedAssetId) return

    const data: AssetRatingCreate = {
      asset_id: selectedAssetId,
      issuer: {
        social_score: scores.social,
        decentralization_score: scores.decentralization,
        technical_score: scores.technical,
      },
      credit: {
        credit_risk_score: scores.credit,
      },
      operational: {
        lindy_score: scores.lindy,
        audit_score: scores.audit,
        transparency_score: scores.transparency,
      },
      rated_by: ratedBy,
      rating_notes: notes || undefined,
    }

    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">New Rating</h1>
          <p className="text-muted-foreground">Create a new asset rating</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-50 p-4 text-red-700 border border-red-200">
          <p className="text-sm">{error}</p>
          <button onClick={() => setError(null)} className="mt-2 text-xs underline hover:no-underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Progress Steps */}
      <div className="flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full ${
                step >= s ? 'bg-primary text-primary-foreground' : 'bg-gray-200'
              }`}
            >
              {step > s ? <Check className="h-4 w-4" /> : s}
            </div>
            {s < 3 && (
              <div
                className={`h-1 w-16 ${step > s ? 'bg-primary' : 'bg-gray-200'}`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Select Asset */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 1: Select Asset</CardTitle>
            <CardDescription>Choose an asset to rate</CardDescription>
          </CardHeader>
          <CardContent>
            <select
              value={selectedAssetId || ''}
              onChange={(e) => setSelectedAssetId(parseInt(e.target.value))}
              className="w-full rounded-md border px-3 py-2"
            >
              <option value="">Select an asset...</option>
              {assets?.items.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} - {asset.name} ({asset.chain})
                </option>
              ))}
            </select>
            <div className="mt-4 flex justify-end">
              <Button onClick={() => setStep(2)} disabled={!selectedAssetId}>
                Next <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Fill Scores */}
      {step === 2 && (
        <div className="space-y-6">
          {/* Issuer Risk */}
          <Card>
            <CardHeader>
              <CardTitle>Issuer Risk</CardTitle>
              <CardDescription>
                Rating: {issuerRisk} (Best of social, decentralization, technical)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ScoreSlider
                label="Social Score"
                value={scores.social}
                onChange={(v) => setScores({ ...scores, social: v })}
                descriptions={SCORE_DESCRIPTIONS.social}
              />
              <ScoreSlider
                label="Decentralization Score"
                value={scores.decentralization}
                onChange={(v) => setScores({ ...scores, decentralization: v })}
                descriptions={SCORE_DESCRIPTIONS.decentralization}
              />
              <ScoreSlider
                label="Technical Score"
                value={scores.technical}
                onChange={(v) => setScores({ ...scores, technical: v })}
                descriptions={SCORE_DESCRIPTIONS.technical}
              />
            </CardContent>
          </Card>

          {/* Credit Risk */}
          <Card>
            <CardHeader>
              <CardTitle>Credit Risk</CardTitle>
              <CardDescription>Rating: {scoreToGrade(scores.credit)}</CardDescription>
            </CardHeader>
            <CardContent>
              <ScoreSlider
                label="Credit Risk Score"
                value={scores.credit}
                onChange={(v) => setScores({ ...scores, credit: v })}
                descriptions={SCORE_DESCRIPTIONS.credit}
              />
            </CardContent>
          </Card>

          {/* Operational Risk */}
          <Card>
            <CardHeader>
              <CardTitle>Operational Risk</CardTitle>
              <CardDescription>
                Rating: {operationalRisk} (Worst of lindy, audit, transparency)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ScoreSlider
                label="Lindy Score"
                value={scores.lindy}
                onChange={(v) => setScores({ ...scores, lindy: v })}
                descriptions={SCORE_DESCRIPTIONS.lindy}
              />
              <ScoreSlider
                label="Audit Score"
                value={scores.audit}
                onChange={(v) => setScores({ ...scores, audit: v })}
                descriptions={SCORE_DESCRIPTIONS.audit}
              />
              <ScoreSlider
                label="Transparency Score"
                value={scores.transparency}
                onChange={(v) => setScores({ ...scores, transparency: v })}
                descriptions={SCORE_DESCRIPTIONS.transparency}
              />
            </CardContent>
          </Card>

          {/* Metadata */}
          <Card>
            <CardHeader>
              <CardTitle>Rating Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Rated By *</label>
                <input
                  value={ratedBy}
                  onChange={(e) => setRatedBy(e.target.value)}
                  placeholder="Your name or identifier"
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Notes</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional rating notes..."
                  rows={3}
                  className="w-full rounded-md border px-3 py-2"
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setStep(1)}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>
            <Button onClick={() => setStep(3)} disabled={!ratedBy}>
              Next <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Step 3: Confirm */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 3: Confirm Rating</CardTitle>
            <CardDescription>Review and submit the rating</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-4">
                {selectedAsset?.symbol} - {selectedAsset?.name}
              </h3>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Issuer Risk</p>
                  <RatingBadge rating={issuerRisk} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Credit Risk</p>
                  <RatingBadge rating={scoreToGrade(scores.credit)} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Operational Risk</p>
                  <RatingBadge rating={operationalRisk} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Final Rating</p>
                  <RatingBadge rating={finalRating} size="lg" />
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-muted-foreground">Vault Eligibility</p>
                <VaultEligibilityBadge eligibility={getVaultEligibility(finalRating)} />
              </div>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>
                <ArrowLeft className="mr-2 h-4 w-4" /> Back
              </Button>
              <Button onClick={handleSubmit} disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Submitting...' : 'Submit Rating'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

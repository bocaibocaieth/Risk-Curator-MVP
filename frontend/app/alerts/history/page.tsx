'use client'

import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { alertsApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import { SEVERITY_COLORS } from '@/types'

export default function AlertHistoryPage() {
  const queryClient = useQueryClient()

  const { data: history, isLoading } = useQuery({
    queryKey: ['alertHistory'],
    queryFn: () => alertsApi.listHistory({ size: 50 }),
  })

  const acknowledgeMutation = useMutation({
    mutationFn: alertsApi.acknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertHistory'] })
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/alerts">
          <Button variant="ghost">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Alert History</h1>
          <p className="text-muted-foreground">Past triggered alerts</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <p>Loading...</p>
          ) : history?.items.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No alert history yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {history?.items.map((alert) => (
                <div
                  key={alert.id}
                  className={`rounded-lg border p-4 ${
                    alert.acknowledged ? 'bg-gray-50' : 'bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{alert.alert_name}</span>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            SEVERITY_COLORS[alert.severity]
                          }`}
                        >
                          {alert.severity}
                        </span>
                        {alert.acknowledged && (
                          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
                            Acknowledged
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {formatDate(alert.triggered_at)}
                      </p>
                      {alert.message && (
                        <pre className="mt-2 whitespace-pre-wrap rounded bg-gray-100 p-2 text-sm">
                          {alert.message}
                        </pre>
                      )}
                    </div>
                    {!alert.acknowledged && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => acknowledgeMutation.mutate(alert.id)}
                        disabled={acknowledgeMutation.isPending}
                      >
                        <Check className="mr-1 h-4 w-4" />
                        Acknowledge
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

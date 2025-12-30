'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ExternalLink } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">System configuration</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Telegram Bot Setup</CardTitle>
            <CardDescription>Configure Telegram notifications</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg bg-gray-50 p-4 text-sm">
              <h4 className="font-medium mb-2">Setup Instructions:</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>
                  Create a bot via{' '}
                  <a
                    href="https://t.me/BotFather"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    @BotFather
                  </a>
                </li>
                <li>Copy the bot token</li>
                <li>Add the bot to your group/channel</li>
                <li>
                  Get Chat ID via{' '}
                  <a
                    href="https://t.me/userinfobot"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    @userinfobot
                  </a>
                </li>
                <li>Set TELEGRAM_BOT_TOKEN in backend .env</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API Documentation</CardTitle>
            <CardDescription>Access the API docs</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" asChild>
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '')}/docs`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Open API Docs
                <ExternalLink className="ml-2 h-4 w-4" />
              </a>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Sources</CardTitle>
            <CardDescription>External data providers</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span>CoinGecko</span>
              <span className="text-sm text-green-600">Connected</span>
            </div>
            <div className="flex items-center justify-between">
              <span>DeFiLlama</span>
              <span className="text-sm text-green-600">Connected</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
            <CardDescription>System information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Version</span>
              <span>0.1.0 (MVP)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Framework</span>
              <span>Next.js 14 + FastAPI</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Rating Model</span>
              <span>Steakhouse Financial</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Sidebar } from '@/components/layout/Sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Risk Curator - DeFi Risk Monitor',
  description: 'DeFi Risk Monitoring and Rating System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-auto bg-gray-50">
              <div className="container mx-auto p-6">
                {children}
              </div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}

import './globals.css'
import { Space_Grotesk } from 'next/font/google'
import { WalletProvider } from '@/components/WalletProvider'

const spaceGrotesk = Space_Grotesk({ subsets: ['latin'] })

export const metadata = {
  title: 'SizeMatters',
  description: 'Connect with successful Solana traders',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={spaceGrotesk.className}>
        <WalletProvider>
          {children}
        </WalletProvider>
      </body>
    </html>
  )
}


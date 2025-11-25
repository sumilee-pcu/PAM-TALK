import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PAM MALL - 디지털 쿠폰 쇼핑몰',
  description: 'Algorand 블록체인 기반 농산물 쇼핑몰',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}

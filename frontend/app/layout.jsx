import './globals.css'

export const metadata = {
  title: 'Enterprise AI Platform | TCS',
  description: 'TCS Enterprise AI Platform - Powered by Claude',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: '#030712', margin: 0, padding: 0 }}>{children}</body>
    </html>
  )
}

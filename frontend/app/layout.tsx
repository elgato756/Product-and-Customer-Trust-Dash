import './globals.css'

export const metadata = {
  title: 'AI Customer Trust & Enterprise Assurance Workflow',
  description: 'Human-in-the-loop customer trust, enterprise assurance, and GRC workflow prototype',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

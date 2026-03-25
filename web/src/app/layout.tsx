import type { Metadata } from 'next';
import './globals.css';
import AppSidebar from '@/components/layout/AppSidebar';

export const metadata: Metadata = {
  title: 'SJDAS v2.0 — Smart Jacquard Design Automation System',
  description: 'The world\'s most capable Indian Jacquard design platform. Screenshot → AI Decode → Production-Ready Loom File in seconds.',
  keywords: 'jacquard, saree design, CAD, loom, textile, AI, Kanjivaram, Banarasi',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{ margin: 0, background: 'var(--bg-base)', color: 'var(--text-primary)', fontFamily: 'var(--font-sans)', display: 'flex', minHeight: '100vh', overflow: 'hidden' }}>
        {/* Global sidebar — hidden only on Studio pages which have their own full-screen UI */}
        <AppSidebar />
        <main style={{ flex: 1, overflow: 'auto', minWidth: 0 }}>
          {children}
        </main>
      </body>
    </html>
  );
}

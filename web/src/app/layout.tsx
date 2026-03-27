import type { Metadata } from 'next';
import './globals.css';
import AppSidebar from '@/components/layout/AppSidebar';
import ContextAwareCopilot from '@/components/ai/ContextAwareCopilot';
import AiAlertStack from '@/components/ai/AiAlertStack';
import AiCommandPalette from '@/components/ai/AiCommandPalette';

export const metadata: Metadata = {
  title: 'SJDAS Enterprise — Smart Jacquard Design Automation',
  description: 'The world\'s most advanced AI-powered Indian Jacquard platform. Seamlessly transition from inspiration to production-ready loom files.',
  keywords: 'jacquard, saree, AI design, CAD, textile automation, Kanjivaram, Banarasi',
  themeColor: '#0a0a0a',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{ margin: 0, color: '#ededed', display: 'flex', minHeight: '100vh', overflow: 'hidden' }}>
        <AppSidebar />
        <main className="app-shell" style={{ flex: 1, overflow: 'auto', minWidth: 0 }}>
          <div className="app-content">{children}</div>
        </main>
        <AiCommandPalette />
        <AiAlertStack />
        <ContextAwareCopilot />
      </body>
    </html>
  );
}

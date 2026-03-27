import Link from 'next/link';
import { ScanLine, ImageIcon, MonitorDot, BarChart3, ArrowRight, Sparkles } from 'lucide-react';

const stats = [
  { label: 'Designs Decoded', value: '0', trend: '+0% this month' },
  { label: 'Loom Files Exported', value: '0', trend: '+0% this month' },
  { label: 'Active Looms', value: '0', trend: '0 running now' },
  { label: 'AI Alerts', value: '0', trend: '0 unresolved' },
];

const quickActions = [
  {
    icon: ScanLine,
    title: 'Decode Screenshot',
    description: 'Upload any saree photo and get a fully decoded, loom-ready design in seconds.',
    href: '/decode',
    accent: 'var(--accent-purple)',
    badge: 'Core AI Feature',
  },
  {
    icon: ImageIcon,
    title: 'Open Studio',
    description: 'Photoshop-grade design editor with SAM2 Magic Trace, repeat engine, and more.',
    href: '/studio/new',
    accent: 'var(--accent-gold)',
  },
  {
    icon: MonitorDot,
    title: 'Factory Monitor',
    description: 'Real-time loom status, job queue management, and alerts for your factory floor.',
    href: '/monitor',
    accent: 'var(--accent-teal)',
  },
  {
    icon: BarChart3,
    title: 'Analytics',
    description: 'Decode trends, loom utilization, AI performance metrics, and business KPIs.',
    href: '/analytics',
    accent: 'var(--accent-blue)',
  },
];

export default function DashboardPage() {
  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div className="badge-purple" style={{ marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Sparkles size={11} />
          <span>SJDAS v2.0 · Production Ready</span>
        </div>
        <h1 className="section-title" style={{ fontSize: 28 }}>
          Welcome back, <span style={{ color: 'var(--accent-gold)' }}>Balaji</span>
        </h1>
        <p className="section-subtitle" style={{ fontSize: 14 }}>
          Minimal, intelligent workspace for textile teams with context-aware AI assistance.
        </p>
      </div>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        {stats.map((s) => (
          <div key={s.label} className="card">
            <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
              {s.value}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{s.label}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{s.trend}</div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>Quick Actions</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 40 }}>
        {quickActions.map((a) => {
          const Icon = a.icon;
          return (
            <Link key={a.title} href={a.href} style={{ textDecoration: 'none' }}>
              <div
                className="card"
                style={{ cursor: 'pointer', transition: 'all 150ms ease-out' }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = a.accent;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 'var(--radius-sm)',
                    background: `rgba(0,0,0,0.3)`, border: `1px solid ${a.accent}44`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon size={18} style={{ color: a.accent }} />
                  </div>
                  {a.badge && <span className="badge-purple">{a.badge}</span>}
                  <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
                <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>{a.title}</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{a.description}</div>
              </div>
            </Link>
          );
        })}
      </div>

      <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>AI Command Center</h2>
      <div className="glass-panel" style={{ padding: 18, marginBottom: 28 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          <div>
            <div className="mono" style={{ color: 'var(--accent-teal)', fontSize: 22, fontWeight: 700 }}>Always On</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Context-aware Copilot for every core workflow</div>
          </div>
          <div>
            <div className="mono" style={{ color: 'var(--accent-blue)', fontSize: 22, fontWeight: 700 }}>Tool Aware</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Guidance adapts to selected tool and stage</div>
          </div>
          <div>
            <div className="mono" style={{ color: 'var(--accent-gold)', fontSize: 22, fontWeight: 700 }}>Smart Defaults</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Recommendations for safer exports and better quality</div>
          </div>
        </div>
      </div>

      {/* Recent Designs Placeholder */}
      <h2 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>Recent Designs</h2>
      <div className="card" style={{ textAlign: 'center', padding: 48 }}>
        <ImageIcon size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 12px' }} />
        <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>No designs yet.</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
          Decode a screenshot or open the studio to create your first design.
        </div>
        <Link href="/decode" style={{ textDecoration: 'none' }}>
          <button className="btn-primary" style={{ marginTop: 16 }}>Decode First Design →</button>
        </Link>
      </div>
    </div>
  );
}

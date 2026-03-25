import { TrendingUp, AlertTriangle } from 'lucide-react';

// Simple bar chart via CSS
function MiniBar({ value, max, color = 'var(--accent-gold)' }: { value: number; max: number; color?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: 'var(--bg-active)', borderRadius: 3 }}>
        <div style={{ width: `${(value / max) * 100}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 600ms ease-out' }} />
      </div>
      <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)', width: 28, textAlign: 'right' }}>{value}</span>
    </div>
  );
}

const kpiCards = [
  { label: 'Decodes This Month', value: '0',   diff: '—' },
  { label: 'Avg Decode Time',    value: '—',   diff: '—' },
  { label: 'BMP Exports',        value: '0',   diff: '—' },
  { label: 'AI Correction Rate', value: '—',   diff: '—' },
];

const styleBreakdown = [
  { name: 'Kanjivaram', count: 0 },
  { name: 'Banarasi',   count: 0 },
  { name: 'Pochampally',count: 0 },
  { name: 'Paithani',   count: 0 },
  { name: 'Other',      count: 0 },
];

export default function AnalyticsPage() {
  return (
    <div style={{ padding: '32px', maxWidth: 1200 }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Analytics</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 4, fontSize: 13 }}>Business metrics, AI performance, and loom utilization trends.</p>
      </div>

      {/* KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
        {kpiCards.map((k) => (
          <div key={k.label} className="card">
            <div className="mono" style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-primary)' }}>{k.value}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{k.label}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6 }}>
              <TrendingUp size={11} style={{ color: 'var(--text-muted)' }} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{k.diff} vs last month</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24 }}>
        {/* Decode trend chart placeholder */}
        <div className="card">
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>Decodes Per Day — Last 30 Days</div>
          <div style={{ height: 160, display: 'flex', alignItems: 'flex-end', gap: 6 }}>
            {Array.from({ length: 30 }, (_, i) => (
              <div key={i} style={{ flex: 1, background: 'var(--bg-active)', borderRadius: '2px 2px 0 0', height: `${Math.random() * 80 + 10}%`, transition: 'height 600ms ease-out' }} />
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: 11, color: 'var(--text-muted)' }}>
            <span>30 days ago</span><span>Today</span>
          </div>
          <div style={{ marginTop: 16, padding: 20, background: 'var(--bg-hover)', borderRadius: 'var(--radius-sm)', textAlign: 'center' }}>
            <AlertTriangle size={20} style={{ color: 'var(--text-muted)', margin: '0 auto 8px' }} />
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>No decode data yet.</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Metrics populate after first decode run.</div>
          </div>
        </div>

        {/* Style Breakdown */}
        <div className="card">
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>Design Style Breakdown</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {styleBreakdown.map((s) => (
              <div key={s.name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  <span>{s.name}</span>
                </div>
                <MiniBar value={s.count} max={Math.max(...styleBreakdown.map(x => x.count), 1)} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

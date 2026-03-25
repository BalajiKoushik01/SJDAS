import { MonitorDot, Wifi, PlusCircle } from 'lucide-react';

export default function MonitorPage() {
  const mockLooms = [
    { id: '1', name: 'Loom #1 — JC5',  status: 'running',     design: 'Kanjivaram_Blue_V3.bmp', progress: 62, picksPerMin: 180 },
    { id: '2', name: 'Loom #2 — JC6',  status: 'idle',        design: null         },
    { id: '3', name: 'Loom #3 — Bonas', status: 'error',      design: null, errorCode: 'E04', errorMessage: 'Thread break at pick 3402, hook 840' },
    { id: '4', name: 'Loom #4 — JC5',  status: 'maintenance', design: null         },
  ];

  const statusColor: Record<string, string> = {
    running:     'var(--accent-teal)',
    idle:        'var(--text-muted)',
    error:       'var(--accent-red)',
    maintenance: 'var(--accent-gold)',
  };
  const statusLabel:  Record<string, string> = {
    running: 'Running', idle: 'Idle', error: 'Error', maintenance: 'Maintenance',
  };

  return (
    <div style={{ padding: '32px', maxWidth: 1200 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Factory Monitor</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4, fontSize: 13 }}>Real-time loom status, job queue, and production alerts.</p>
        </div>
        <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <PlusCircle size={14} /> Add Loom
        </button>
      </div>

      {/* Summary Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
        {[
          { label: 'Running', value: '1', color: 'var(--accent-teal)' },
          { label: 'Idle', value: '1', color: 'var(--text-muted)' },
          { label: 'Errors', value: '1', color: 'var(--accent-red)' },
          { label: 'Maintenance', value: '1', color: 'var(--accent-gold)' },
        ].map((s) => (
          <div key={s.label} className="card" style={{ textAlign: 'center' }}>
            <div className="mono" style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Loom Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
        {mockLooms.map((loom) => (
          <div key={loom.id} className={`card ${loom.status === 'running' ? 'card-active' : ''}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: statusColor[loom.status],
                  ...(loom.status === 'running' ? { boxShadow: `0 0 8px var(--accent-teal)`, animation: 'pulse-green 2s infinite' } : {}),
                  ...(loom.status === 'error'   ? { boxShadow: `0 0 8px var(--accent-red)`,   animation: 'pulse-red 1.2s infinite' } : {}),
                }} />
                <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{loom.name}</span>
              </div>
              <span className={loom.status === 'running' ? 'badge-teal' : loom.status === 'error' ? 'badge-red' : 'badge-gold'}>
                {statusLabel[loom.status]}
              </span>
            </div>

            {loom.status === 'running' && (
              <>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
                  {loom.design} · <span className="mono" style={{ color: 'var(--accent-gold)' }}>{loom.picksPerMin} picks/min</span>
                </div>
                <div className="progress-track" style={{ marginBottom: 4 }}>
                  <div className="progress-fill-teal" style={{ width: `${loom.progress}%` }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)' }}>
                  <span>{loom.progress}% complete</span><span>ETA: ~24 min</span>
                </div>
              </>
            )}

            {loom.status === 'error' && (
              <div style={{ background: 'rgba(240,76,95,0.1)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', fontSize: 12, color: 'var(--accent-red)' }}>
                <span className="mono" style={{ fontWeight: 600 }}>{loom.errorCode}</span> — {loom.errorMessage}
              </div>
            )}

            {loom.status === 'idle' && (
              <button className="btn-primary" style={{ width: '100%', marginTop: 4 }}>Send Job →</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

'use client';

import { useStudioStore, type SareeStyle } from '@/store/useStudioStore';

const STYLES: SareeStyle[] = ['Kanjivaram', 'Banarasi', 'Pochampally', 'Paithani', 'Other'];

export default function DecodeControls() {
  const { hooks, kalis, colorCount, styleOverride, setMechanicalSpecs, setColorCount, setStyleOverride } = useStudioStore();

  return (
    <div className="card">
      <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>
        Decode Parameters
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Style Override */}
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
            Style Override <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>(auto-detected)</span>
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            <button
              onClick={() => setStyleOverride(null)}
              className={styleOverride === null ? 'badge-gold' : 'badge-teal'}
              style={{ cursor: 'pointer', border: 'none' }}
            >
              Auto
            </button>
            {STYLES.map((s) => (
              <button
                key={s}
                onClick={() => setStyleOverride(styleOverride === s ? null : s)}
                className={styleOverride === s ? 'badge-gold' : undefined}
                style={{
                  cursor: 'pointer', border: '1px solid var(--border-hover)',
                  background: styleOverride === s ? undefined : 'transparent',
                  color: styleOverride === s ? undefined : 'var(--text-secondary)',
                  borderRadius: 20, padding: '4px 10px', fontSize: 11, fontWeight: 500,
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Hook Count */}
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span>Hook Count</span>
            <span className="mono" style={{ color: 'var(--accent-gold)' }}>{hooks}</span>
          </label>
          <input type="range" min={1000} max={4000} step={100} value={hooks}
            onChange={(e) => setMechanicalSpecs(Number(e.target.value), kalis)}
            style={{ width: '100%', accentColor: 'var(--accent-gold)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            <span>1000</span><span>4000</span>
          </div>
        </div>

        {/* Color Count */}
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span>Yarn Colors</span>
            <span className="mono" style={{ color: 'var(--accent-gold)' }}>{colorCount}</span>
          </label>
          <input type="range" min={2} max={64} step={1} value={colorCount}
            onChange={(e) => setColorCount(Number(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--accent-gold)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            <span>2 colors</span><span>64 colors</span>
          </div>
        </div>

        {/* Kalis */}
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span>Kali Count</span>
            <span className="mono" style={{ color: 'var(--accent-gold)' }}>{kalis}</span>
          </label>
          <input type="range" min={1} max={12} step={1} value={kalis}
            onChange={(e) => setMechanicalSpecs(hooks, Number(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--accent-gold)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            <span>1</span><span>12</span>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useStudioStore } from '@/store/useStudioStore';
import { Play, Download, ChevronDown, Cloud, CheckCircle, Loader2, Grid3x3 } from 'lucide-react';
import { useState } from 'react';
import { apiV1 } from '@/lib/runtime';

const EXPORT_FORMATS = ['BMP (Loom)', 'JC5 / Stäubli', 'WIF', 'SVG', 'DXF', 'PDF Sheet', 'PNG 300DPI'];

export default function StudioHeader() {
  const { hooks, kalis, setMechanicalSpecs, taskId, wsMessage, showGrid, setShowGrid } = useStudioStore();
  const [exporting, setExporting] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);

  const handleExport = async (format: string) => {
    setExporting(true);
    setExportOpen(false);
    try {
      const res = await fetch(apiV1('/generate-loom-file-async'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_id: 'studio-active', hooks, kali_count: kalis, picks_height: 8000, format }),
      });
      const data = await res.json();
      if (data.task_id) useStudioStore.getState().setTaskId(data.task_id);
    } finally {
      setTimeout(() => setExporting(false), 2000);
    }
  };

  return (
    <header style={{
      height: 52, width: '100%', display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', padding: '0 16px',
      background: 'rgba(15,17,23,0.95)', backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
      position: 'absolute', top: 0, left: 0, right: 0, zIndex: 60,
    }}>
      {/* Left: Brand + breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
          <span style={{ color: 'var(--accent-gold)' }}>SJ</span>DAS Studio
        </span>
        <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>/</span>
        <span className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Untitled Design</span>
      </div>

      {/* Center: Mechanical Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <label style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Hooks</label>
          <input
            type="number" value={hooks} min={1000} max={4000} step={100}
            onChange={(e) => setMechanicalSpecs(Number(e.target.value), kalis)}
            className="mono"
            style={{
              width: 64, height: 28, background: 'var(--bg-hover)', border: '1px solid var(--border-hover)',
              borderRadius: 'var(--radius-sm)', color: 'var(--accent-gold)', textAlign: 'center',
              fontSize: 13, fontFamily: 'var(--font-mono)', outline: 'none', padding: 0,
            }}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <label style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Kalis</label>
          <input
            type="number" value={kalis} min={1} max={12}
            onChange={(e) => setMechanicalSpecs(hooks, Number(e.target.value))}
            className="mono"
            style={{
              width: 40, height: 28, background: 'var(--bg-hover)', border: '1px solid var(--border-hover)',
              borderRadius: 'var(--radius-sm)', color: 'var(--accent-gold)', textAlign: 'center',
              fontSize: 13, fontFamily: 'var(--font-mono)', outline: 'none', padding: 0,
            }}
          />
        </div>

        {/* Grid Toggle */}
        <button
          onClick={() => setShowGrid(!showGrid)}
          title="Toggle Grid"
          style={{
            width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
            borderRadius: 'var(--radius-sm)', border: 'none', cursor: 'pointer',
            background: showGrid ? 'var(--accent-gold-dim)' : 'var(--bg-hover)',
            color: showGrid ? 'var(--accent-gold)' : 'var(--text-muted)',
          }}
        >
          <Grid3x3 size={14} />
        </button>

        {/* Cloud Status */}
        {taskId && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-muted)' }}>
            <Cloud size={12} />
            <span>{wsMessage}</span>
          </div>
        )}
      </div>

      {/* Right: Export */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, position: 'relative' }}>
        <button
          onClick={() => setExportOpen(!exportOpen)}
          className="btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: 6, height: 32, padding: '0 12px', fontSize: 12 }}
        >
          {exporting ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} /> : <Download size={13} />}
          Export
          <ChevronDown size={12} />
        </button>

        {exportOpen && (
          <div style={{
            position: 'absolute', top: 36, right: 0, zIndex: 200,
            background: 'var(--bg-elevated)', border: '1px solid var(--border-hover)',
            borderRadius: 'var(--radius-md)', padding: 4, minWidth: 160,
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          }}>
            {EXPORT_FORMATS.map((f) => (
              <button key={f} onClick={() => handleExport(f)} style={{
                display: 'block', width: '100%', padding: '8px 12px', textAlign: 'left',
                background: 'none', border: 'none', cursor: 'pointer',
                color: 'var(--text-secondary)', fontSize: 13, borderRadius: 'var(--radius-sm)',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-hover)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
              >{f}</button>
            ))}
          </div>
        )}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
}

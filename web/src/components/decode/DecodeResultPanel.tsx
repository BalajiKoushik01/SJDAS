'use client';

import { useStudioStore } from '@/store/useStudioStore';
import { ExternalLink, Eye, EyeOff, AlertTriangle, CheckCircle, Layers, Palette } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

export default function DecodeResultPanel() {
  const decodeResult = useStudioStore((s) => s.decodeResult);
  const [hiddenLayers, setHiddenLayers] = useState<Set<string>>(new Set());

  if (!decodeResult) return null;

  const toggleLayer = (id: string) =>
    setHiddenLayers((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });

  return (
    <div className="fade-in-up" style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Analysis Card */}
      <div className="card" style={{ borderColor: 'var(--accent-gold)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
          <div>
            <span className="badge-gold" style={{ marginBottom: 8, display: 'inline-block' }}>{decodeResult.styleLabel}</span>
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>
              AI Analysis Card
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="mono" style={{ fontSize: 20, fontWeight: 700, color: 'var(--accent-gold)' }}>
              {Math.round(decodeResult.styleConfidence * 100)}%
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>confidence</div>
          </div>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.5 }}>
          {decodeResult.analysisCard}
        </p>
        {decodeResult.weaveRecommendation && (
          <div style={{ background: 'var(--bg-hover)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', fontSize: 12, color: 'var(--text-secondary)' }}>
            💡 {decodeResult.weaveRecommendation}
          </div>
        )}
        {decodeResult.alert && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginTop: 10, background: 'rgba(240,76,95,0.1)', borderRadius: 'var(--radius-sm)', padding: '8px 12px' }}>
            <AlertTriangle size={14} style={{ color: 'var(--accent-red)', marginTop: 1, flexShrink: 0 }} />
            <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{decodeResult.alert}</span>
          </div>
        )}
      </div>

      {/* Motifs & Colors */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Motifs */}
        <div className="card">
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12, display: 'flex', gap: 6 }}>
            <Layers size={12} style={{ color: 'var(--accent-purple)' }} /> Motifs
          </div>
          {decodeResult.motifs?.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {decodeResult.motifs.map((m, i) => (
                <span key={i} className="badge-purple">
                  {m.class} <span className="mono" style={{ opacity: 0.7 }}>{Math.round(m.confidence * 100)}%</span>
                </span>
              ))}
            </div>
          ) : <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>None detected</span>}
        </div>

        {/* Color Palette */}
        <div className="card">
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12, display: 'flex', gap: 6 }}>
            <Palette size={12} style={{ color: 'var(--accent-gold)' }} /> Yarn Palette
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {decodeResult.colors?.map((c) => (
              <div key={c.id} title={`${c.name} • ${c.hex}`}>
                <div style={{ width: 28, height: 28, borderRadius: 'var(--radius-sm)', background: c.hex, border: '2px solid var(--border-hover)' }} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Layers */}
      {decodeResult.layers?.length > 0 && (
        <div className="card">
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
            SVG Layers
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {decodeResult.layers.map((l) => (
              <div key={l.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 'var(--radius-sm)', background: 'var(--bg-hover)' }}>
                <button onClick={() => toggleLayer(l.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: hiddenLayers.has(l.id) ? 'var(--text-muted)' : 'var(--text-primary)', padding: 0 }}>
                  {hiddenLayers.has(l.id) ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
                <span style={{ fontSize: 13, color: 'var(--text-primary)', flex: 1 }}>{l.name}</span>
                {l.region && <span className="badge-teal" style={{ padding: '2px 6px', fontSize: 10 }}>{l.region}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Float Check */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>Float Validation</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Max float length check against hook limit</div>
        </div>
        {decodeResult.floatCheckPassed ? (
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--accent-teal)' }}>
            <CheckCircle size={16} /> <span style={{ fontSize: 13, fontWeight: 600 }}>Passed</span>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--accent-red)' }}>
            <AlertTriangle size={16} /> <span style={{ fontSize: 13, fontWeight: 600 }}>Review Required</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12 }}>
        <Link href="/studio/decoded-1" style={{ textDecoration: 'none', flex: 1 }}>
          <button className="btn-primary" style={{ width: '100%' }}>Open in Studio →</button>
        </Link>
        <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <ExternalLink size={14} /> Export BMP
        </button>
      </div>
    </div>
  );
}

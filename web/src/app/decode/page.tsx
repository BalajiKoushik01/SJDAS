'use client';

import { useStudioStore } from '@/store/useStudioStore';
import UploadZone from '@/components/decode/UploadZone';
import PipelineProgress from '@/components/decode/PipelineProgress';
import DecodeControls from '@/components/decode/DecodeControls';
import DecodeResultPanel from '@/components/decode/DecodeResultPanel';
import { Zap, Brain } from 'lucide-react';
import { apiV1 } from '@/lib/runtime';

export default function DecodePage() {
  const { uploadedFile, isDecoding, decodeResult, hooks, kalis, colorCount, styleOverride,
          startDecoding, setTaskId } = useStudioStore();

  const handleDecode = async () => {
    if (!uploadedFile) return;
    startDecoding();

    try {
      const form = new FormData();
      form.append('file', uploadedFile);
      form.append('hook_count', String(hooks));
      form.append('ends_ppi', String(80));
      form.append('color_count', String(colorCount));
      if (styleOverride) form.append('style_override', styleOverride);

      const res = await fetch(apiV1('/decode-async'), {
        method: 'POST',
        body: form,
      });
      const { task_id } = await res.json();
      if (task_id) setTaskId(task_id);
    } catch {
      useStudioStore.getState().finishDecoding();
    }
  };

  return (
    <div style={{ padding: '32px', maxWidth: 1000, margin: '0 auto' }}>
      {/* Page Header */}
      <div style={{ marginBottom: 32 }}>
        <div className="badge-purple" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
          <Brain size={11} /> AI Decode Pipeline
        </div>
        <h1 style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', margin: 0, lineHeight: 1.2 }}>
          Screenshot → Loom File
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: 14, maxWidth: 600 }}>
          Upload any saree photo — blurry, cropped, or WhatsApp-forwarded. SJDAS automatically
          segments regions, traces motifs, extracts yarn colors, and generates a loom-ready BMP.
          No competitor has this.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24, alignItems: 'flex-start' }}>
        {/* Left: Upload + Progress + Results */}
        <div>
          <UploadZone />
          <PipelineProgress />
          {decodeResult && <DecodeResultPanel />}
        </div>

        {/* Right: Controls + Action */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <DecodeControls />

          <button
            className="btn-primary"
            onClick={handleDecode}
            disabled={!uploadedFile || isDecoding}
            style={{
              width: '100%', height: 44, fontSize: 14,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              opacity: (!uploadedFile || isDecoding) ? 0.5 : 1,
              cursor: (!uploadedFile || isDecoding) ? 'not-allowed' : 'pointer',
            }}
          >
            <Zap size={16} fill="currentColor" />
            {isDecoding ? 'AI Decoding...' : 'Run Decode Pipeline'}
          </button>

          {/* Robustness Info */}
          <div className="card" style={{ padding: 14 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
              Pipeline Handles
            </div>
            {[
              'Images as low as 320×240px (auto-upscale)',
              'Off-angle photos up to 30° tilt',
              'JPEG compression artifacts (denoise)',
              'WhatsApp & screenshot compression',
              'Partial / cropped saree images',
            ].map((t) => (
              <div key={t} style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'flex', gap: 6 }}>
                <span style={{ color: 'var(--accent-teal)' }}>✓</span> {t}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

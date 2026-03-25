'use client';

import { useEffect, useRef } from 'react';
import { useStudioStore } from '@/store/useStudioStore';
import { CheckCircle, Loader2, Circle } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 'preprocess',  label: 'Preprocess',         desc: 'Upscaling, deskew, denoise' },
  { id: 'segment',     label: 'SAM2 Segmentation',   desc: 'Body / Border / Pallu / Motifs' },
  { id: 'detect',      label: 'Motif Detection',     desc: 'YOLOv8 motif bounding boxes' },
  { id: 'vectorize',   label: 'Vectorize',           desc: 'VTracer → SVG layer output' },
  { id: 'colors',      label: 'Color Separation',    desc: 'KMeans palette extraction' },
  { id: 'weave',       label: 'Weave Matrix',        desc: 'Structure + float validation' },
];

function getStepState(stepIndex: number, currentProgress: number): 'done' | 'active' | 'pending' {
  const stepThreshold = ((stepIndex + 1) / PIPELINE_STEPS.length) * 100;
  const prevThreshold = (stepIndex / PIPELINE_STEPS.length) * 100;
  if (currentProgress >= stepThreshold) return 'done';
  if (currentProgress > prevThreshold) return 'active';
  return 'pending';
}

export default function PipelineProgress() {
  const decodeProgress = useStudioStore((s) => s.decodeProgress);
  const decodeStepMessage = useStudioStore((s) => s.decodeStepMessage);
  const isDecoding = useStudioStore((s) => s.isDecoding);
  const taskId = useStudioStore((s) => s.taskId);
  const setDecodeProgress = useStudioStore((s) => s.setDecodeProgress);
  const setDecodeResult  = useStudioStore((s) => s.setDecodeResult);
  const finishDecoding   = useStudioStore((s) => s.finishDecoding);

  const wsRef = useRef<WebSocket | null>(null);

  // Wire WebSocket when taskId is set
  useEffect(() => {
    if (!taskId) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/${taskId}`);
    wsRef.current = ws;

    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.status === 'progress') {
        const { progress, message } = msg.meta || {};
        setDecodeProgress(progress ?? decodeProgress, message);
      } else if (msg.status === 'success') {
        setDecodeProgress(100, 'Decode Complete!');
        setDecodeResult(msg.result);
        finishDecoding();
        ws.close();
      } else if (msg.status === 'error') {
        finishDecoding();
        ws.close();
      }
    };

    return () => { ws.readyState === WebSocket.OPEN && ws.close(); };
  }, [taskId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!isDecoding && decodeProgress === 0) return null;

  return (
    <div className="card fade-in-up" style={{ marginTop: 24 }}>
      {/* Overall progress bar */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            {decodeProgress === 100 ? 'Decode Complete' : 'AI Pipeline Running...'}
          </span>
          <span className="mono" style={{ fontSize: 12, color: 'var(--accent-gold)' }}>{decodeProgress}%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill-gold" style={{ width: `${decodeProgress}%` }} />
        </div>
        {decodeStepMessage && (
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>{decodeStepMessage}</div>
        )}
      </div>

      {/* Step-by-step list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {PIPELINE_STEPS.map((step, i) => {
          const state = getStepState(i, decodeProgress);
          return (
            <div
              key={step.id}
              className={i > 0 ? 'fade-in-up' : undefined}
              style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                background: state === 'active' ? 'var(--accent-gold-dim)' : 'transparent',
                border: `1px solid ${state === 'active' ? 'rgba(201,168,76,0.3)' : 'transparent'}`,
                transition: 'all 200ms ease-out',
                animationDelay: `${i * 150}ms`,
              }}
            >
              {state === 'done'   && <CheckCircle size={16} style={{ color: 'var(--accent-teal)', flexShrink: 0 }} />}
              {state === 'active' && <Loader2 size={16} style={{ color: 'var(--accent-gold)', flexShrink: 0, animation: 'spin 1s linear infinite' }} />}
              {state === 'pending'&& <Circle size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />}
              <div>
                <div style={{ fontSize: 13, fontWeight: state === 'active' ? 600 : 400, color: state === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                  {step.label}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{step.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

'use client';

import { useStudioStore } from '@/store/useStudioStore';
import { BellRing } from 'lucide-react';

export default function AiAlertStack() {
  const alerts = useStudioStore((state) => state.aiAlerts);
  const dismiss = useStudioStore((state) => state.dismissAIAlert);

  if (alerts.length === 0) return null;

  return (
    <div style={{ position: 'fixed', right: 16, top: 16, zIndex: 90, width: 320, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {alerts.slice(0, 3).map((alert) => (
        <div key={alert.id} className="glass-panel" style={{ padding: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
              <BellRing size={14} style={{ marginTop: 2, color: 'var(--accent-blue)' }} />
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{alert.message}</span>
            </div>
            {alert.dismissible && (
              <button className="btn-secondary" onClick={() => dismiss(alert.id)} style={{ height: 24, padding: '0 7px' }}>
                x
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

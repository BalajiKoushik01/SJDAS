'use client';

import { useEffect, useMemo, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Command, Sparkles } from 'lucide-react';
import { useStudioStore } from '@/store/useStudioStore';

type CommandAction = {
  id: string;
  label: string;
  run: () => void;
};

export default function AiCommandPalette() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const setActiveTool = useStudioStore((s) => s.setActiveTool);
  const addAlert = useStudioStore((s) => s.addAIAlert);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setOpen((state) => !state);
      }
      if (event.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const actions = useMemo<CommandAction[]>(
    () => [
      {
        id: 'goto-decode',
        label: 'Go to Decode Workspace',
        run: () => router.push('/decode'),
      },
      {
        id: 'goto-studio',
        label: 'Open Studio',
        run: () => router.push('/studio/new'),
      },
      {
        id: 'tool-ai-trace',
        label: 'Switch to AI Trace Tool',
        run: () => {
          setActiveTool('ai-trace');
          addAlert({
            id: 'cmd_ai_trace',
            severity: 'success',
            message: 'AI Trace selected from command palette.',
            dismissible: true,
          });
        },
      },
      {
        id: 'tool-heal',
        label: 'Switch to Smart Heal Tool',
        run: () => {
          setActiveTool('heal');
          addAlert({
            id: 'cmd_ai_heal',
            severity: 'success',
            message: 'Smart Heal selected from command palette.',
            dismissible: true,
          });
        },
      },
      {
        id: 'copilot-hint',
        label: 'Show AI Optimization Hint',
        run: () => {
          const page = pathname.includes('/decode') ? 'decode' : pathname.includes('/studio') ? 'studio' : 'dashboard';
          addAlert({
            id: 'cmd_hint',
            severity: 'info',
            message: `Copilot hint (${page}): prioritize clean inputs, keep palette compact, and validate before export.`,
            dismissible: true,
          });
        },
      },
    ],
    [router, setActiveTool, addAlert, pathname],
  );

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="btn-secondary"
        style={{ position: 'fixed', left: 16, bottom: 16, zIndex: 80, display: 'flex', gap: 8, alignItems: 'center' }}
      >
        <Command size={14} />
        AI Commands
      </button>
    );
  }

  return (
    <div
      className="glass-panel"
      style={{
        position: 'fixed',
        left: '50%',
        top: '20%',
        transform: 'translateX(-50%)',
        zIndex: 100,
        width: 560,
        maxWidth: '92vw',
        padding: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} />
        <strong style={{ fontSize: 13 }}>AI Command Palette</strong>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Ctrl/Cmd + K</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {actions.map((action) => (
          <button
            key={action.id}
            className="btn-secondary"
            style={{ justifyContent: 'flex-start', display: 'flex', width: '100%', height: 34 }}
            onClick={() => {
              action.run();
              setOpen(false);
            }}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}

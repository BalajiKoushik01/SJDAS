'use client';

import { useEffect, useMemo, useState } from 'react';
import { Brain, Sparkles, Lightbulb, Wand2, ShieldCheck } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { useStudioStore, type ToolId } from '@/store/useStudioStore';
import { apiV1 } from '@/lib/runtime';

type CopilotSuggestion = {
  title: string;
  message: string;
  actionLabel?: string;
  action?: () => Promise<void>;
};

const TOOL_HINTS: Partial<Record<ToolId, string>> = {
  'magic-wand': 'Try reducing color count before using Magic Wand to improve selection precision.',
  'quick-select': 'Quick Select works best after zooming in to motif edges.',
  'ai-trace': 'Use AI Trace for motif extraction and convert to clean vector layers.',
  heal: 'Smart Healing works best with small target regions and repeated motif structures.',
  'clone-stamp': 'Sample from a nearby region with similar thread density for seamless results.',
  mirror: 'Mirror Kali keeps panel symmetry consistent across full saree width.',
};

export default function ContextAwareCopilot() {
  const pathname = usePathname();
  const activeTool = useStudioStore((state) => state.activeTool);
  const decodeProgress = useStudioStore((state) => state.decodeProgress);
  const hooks = useStudioStore((state) => state.hooks);
  const kalis = useStudioStore((state) => state.kalis);
  const [isOpen, setIsOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [assistantNote, setAssistantNote] = useState<string>('');
  const [remoteHint, setRemoteHint] = useState<string>('');

  useEffect(() => {
    const stored = localStorage.getItem('sjdas_copilot_last_note');
    if (stored) setAssistantNote(stored);
  }, []);

  useEffect(() => {
    if (!pathname.includes('/studio') && !pathname.includes('/decode')) {
      setIsOpen(false);
    }
  }, [pathname]);

  const suggestion = useMemo<CopilotSuggestion>(() => {
    if (pathname.includes('/decode')) {
      if (decodeProgress > 0 && decodeProgress < 100) {
        return {
          title: 'Decode Running',
          message: `Pipeline progress is ${decodeProgress}%. I am monitoring for quality and float-risk signals in the background.`,
        };
      }
      return {
        title: 'Decode Assistant',
        message: 'Upload an image and I will guide settings for hooks, palette compression, and export readiness.',
        actionLabel: 'Quick Optimize Settings',
        action: async () => {
          setAssistantNote('Recommended: hooks 1200+, 6-8 colors, and style override enabled for stable outputs.');
        },
      };
    }

    const toolHint = TOOL_HINTS[activeTool] || 'Use this tool with AI guidance for faster results and fewer manual retries.';
    return {
      title: 'Studio Copilot',
      message: `${toolHint} Current mechanical profile: ${hooks} hooks, ${kalis} kalis.`,
      actionLabel: activeTool === 'ai-trace' || activeTool === 'heal' ? 'Run AI Tool Health Check' : 'Get Pro Tip',
      action: async () => {
        setIsLoading(true);
        try {
          const response = await fetch(apiV1('/health'));
          if (response.ok) {
            setAssistantNote('AI backend is reachable. You can use intelligent tools confidently.');
          } else {
            setAssistantNote('AI backend health check failed. Please verify API connectivity.');
          }
        } catch {
          setAssistantNote('AI backend is not reachable right now. I will keep using local guidance.');
        } finally {
          setIsLoading(false);
        }
      },
    };
  }, [pathname, decodeProgress, activeTool, hooks, kalis]);

  useEffect(() => {
    const token = localStorage.getItem('sjdas_token') || '';
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    const page = pathname.includes('/decode') ? 'decode' : pathname.includes('/studio') ? 'studio' : 'other';
    if (page === 'other') return;
    fetch(apiV1('/ai/context-assist'), {
      method: 'POST',
      headers,
      body: JSON.stringify({
        page,
        active_tool: activeTool,
        decode_progress: decodeProgress,
        hooks,
        kalis,
      }),
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.message) setRemoteHint(data.message);
      })
      .catch(() => {
        setRemoteHint('');
      });
  }, [pathname, activeTool, decodeProgress, hooks, kalis]);

  useEffect(() => {
    if (assistantNote) {
      localStorage.setItem('sjdas_copilot_last_note', assistantNote);
    }
  }, [assistantNote]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn-secondary"
        style={{ position: 'fixed', right: 16, bottom: 16, zIndex: 80, display: 'flex', gap: 8, alignItems: 'center' }}
      >
        <Brain size={14} />
        AI Copilot
      </button>
    );
  }

  return (
    <div
      className="glass-panel"
      style={{
        position: 'fixed',
        right: 16,
        bottom: 16,
        zIndex: 80,
        width: 330,
        padding: 14,
        boxShadow: '0 10px 34px rgba(0,0,0,0.45)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} />
          <strong style={{ fontSize: 13 }}>{suggestion.title}</strong>
        </div>
        <button onClick={() => setIsOpen(false)} className="btn-secondary" style={{ height: 26, padding: '0 8px' }}>
          Hide
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, color: 'var(--text-secondary)', fontSize: 12, lineHeight: 1.5 }}>
        <Lightbulb size={13} style={{ marginTop: 2, flexShrink: 0 }} />
        <span>{suggestion.message}</span>
      </div>

      {remoteHint && (
        <div style={{ marginTop: 8, fontSize: 12, color: 'var(--accent-blue)' }}>
          {remoteHint}
        </div>
      )}

      {assistantNote && (
        <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-primary)', display: 'flex', gap: 8 }}>
          <ShieldCheck size={13} style={{ marginTop: 2, color: 'var(--accent-teal)', flexShrink: 0 }} />
          <span>{assistantNote}</span>
        </div>
      )}

      {suggestion.actionLabel && suggestion.action && (
        <button
          className="btn-primary"
          onClick={() => suggestion.action?.()}
          disabled={isLoading}
          style={{ marginTop: 12, width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 6 }}
        >
          <Wand2 size={14} />
          {isLoading ? 'Checking...' : suggestion.actionLabel}
        </button>
      )}
    </div>
  );
}

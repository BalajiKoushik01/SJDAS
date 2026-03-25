'use client';

import { useStudioStore } from '@/store/useStudioStore';
import type { ToolId } from '@/store/useStudioStore';
import { motion } from 'framer-motion';
import {
  MousePointer2, Lasso, Wand2, Crosshair,
  Brush, Pencil, Eraser, PaintBucket, Blend,
  Copy, Pipette, ZoomIn, Hand,
  Sparkles, Bandage, RefreshCw,
  ChevronDown,
} from 'lucide-react';

interface ToolGroup {
  label: string;
  tools: Array<{ id: ToolId; icon: React.ElementType; label: string; badge?: string }>;
}

const TOOL_GROUPS: ToolGroup[] = [
  {
    label: 'Selection',
    tools: [
      { id: 'cursor',       icon: MousePointer2, label: 'Move / Select' },
      { id: 'lasso',        icon: Lasso,         label: 'Lasso Select' },
      { id: 'magic-wand',   icon: Wand2,         label: 'Magic Wand' },
      { id: 'quick-select', icon: Crosshair,     label: 'Quick Select' },
    ],
  },
  {
    label: 'AI Tools',
    tools: [
      { id: 'ai-trace', icon: Sparkles, label: 'SAM 2 Magic Trace', badge: 'AI' },
      { id: 'heal',     icon: Bandage,  label: 'Smart Healing Brush', badge: 'AI' },
    ],
  },
  {
    label: 'Drawing',
    tools: [
      { id: 'brush',       icon: Brush,       label: 'Brush' },
      { id: 'pencil',      icon: Pencil,      label: 'Pencil (Aliased)' },
      { id: 'eraser',      icon: Eraser,      label: 'Eraser' },
      { id: 'fill',        icon: PaintBucket, label: 'Fill (Flood)' },
      { id: 'gradient',    icon: Blend,       label: 'Gradient Fill' },
      { id: 'clone-stamp', icon: Copy,        label: 'Clone Stamp' },
      { id: 'mirror',      icon: RefreshCw,   label: 'Mirror Kali' },
    ],
  },
  {
    label: 'View',
    tools: [
      { id: 'eyedropper', icon: Pipette, label: 'Eyedropper' },
      { id: 'zoom',       icon: ZoomIn,  label: 'Zoom' },
      { id: 'hand',       icon: Hand,    label: 'Pan' },
    ],
  },
];

export default function GlassToolbox() {
  const { activeTool, setActiveTool } = useStudioStore();

  return (
    <div style={{
      position: 'absolute', left: 12, top: 12, bottom: 12, zIndex: 50,
      display: 'flex', flexDirection: 'column', gap: 2,
      padding: '8px 6px',
      background: 'rgba(15,17,23,0.85)',
      backdropFilter: 'blur(16px)',
      border: '1px solid var(--border-hover)',
      borderRadius: 'var(--radius-md)',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      overflowY: 'auto',
      width: 48,
    }}>
      {TOOL_GROUPS.map((group, gi) => (
        <div key={group.label}>
          {gi > 0 && <div style={{ height: 1, background: 'var(--border)', margin: '4px 0' }} />}
          {group.tools.map((t) => {
            const Icon = t.icon;
            const isActive = activeTool === t.id;
            return (
              <motion.button
                key={t.id}
                title={t.label}
                onClick={() => setActiveTool(t.id)}
                whileHover={{ scale: 1.1, backgroundColor: isActive ? 'var(--accent-gold-dim)' : 'var(--bg-hover)' }}
                whileTap={{ scale: 0.9 }}
                animate={{
                  backgroundColor: isActive ? 'var(--accent-gold-dim)' : 'transparent',
                  color: isActive ? 'var(--accent-gold)' : 'var(--text-muted)',
                  boxShadow: isActive ? 'inset 0 0 0 1px rgba(201,168,76,0.4)' : 'inset 0 0 0 0px transparent',
                }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                style={{
                  width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  borderRadius: 'var(--radius-sm)', cursor: 'pointer', border: 'none',
                  position: 'relative',
                }}
              >
                <Icon size={15} strokeWidth={isActive ? 2.5 : 2} />
                {t.badge && (
                  <motion.span
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    style={{
                      position: 'absolute', top: 2, right: 2, fontSize: 6, lineHeight: 1,
                      background: 'var(--accent-purple)', color: '#fff',
                      borderRadius: 3, padding: '1px 2px', fontWeight: 700,
                    }}
                  >
                    AI
                  </motion.span>
                )}
              </motion.button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

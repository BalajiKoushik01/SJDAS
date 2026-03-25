'use client';

import { useStudioStore } from '@/store/useStudioStore';
import { MousePointer2, Wand2, PaintBucket, Bandage, Copy } from 'lucide-react';
import { cn } from '@/lib/utils'; // standard shadcn class merger

export default function GlassToolbox() {
  const activeTool = useStudioStore((state) => state.activeTool);
  const setActiveTool = useStudioStore((state) => state.setActiveTool);

  const tools = [
    { id: 'cursor', icon: MousePointer2, label: 'Selection' },
    { id: 'ai-trace', icon: Wand2, label: 'SAM 2 Magic Trace' },
    { id: 'heal', icon: Bandage, label: 'Auto-Heal Seams' },
    { id: 'bucket', icon: PaintBucket, label: 'Index Color Swap' },
    { id: 'mirror', icon: Copy, label: 'Mirror Kali' }
  ];

  return (
    <div className="absolute left-6 top-24 z-50 flex flex-col gap-3 p-2 bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 shadow-2xl rounded-2xl">
      {tools.map((t) => {
        const Icon = t.icon;
        const isActive = activeTool === t.id;
        return (
          <button
            key={t.id}
            onClick={() => setActiveTool(t.id as any)}
            title={t.label}
            className={cn(
              "p-3 rounded-xl transition-all duration-200 relative group flex items-center justify-center",
              isActive 
                ? "bg-[#38bdf8]/10 text-[#38bdf8] shadow-[inset_0_0_10px_rgba(56,189,248,0.2)] border border-[#38bdf8]/50" 
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent"
            )}
          >
            <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            
            {/* Tooltip */}
            <span className="absolute left-14 bg-slate-800 text-slate-200 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-slate-700 pointer-events-none">
              {t.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}

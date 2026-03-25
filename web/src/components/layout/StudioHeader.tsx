'use client';

import { useStudioStore } from '@/store/useStudioStore';
import { Play } from 'lucide-react';

export default function StudioHeader() {
  const hooks = useStudioStore((state) => state.hooks);
  const kalis = useStudioStore((state) => state.kalis);
  const setMechanicalSpecs = useStudioStore((state) => state.setMechanicalSpecs);
  const setTaskId = useStudioStore((state) => state.setTaskId);

  const handleRunMachine = async () => {
    // Fire the POST request to FastAPI to kick off Celery Task
    const res = await fetch('http://localhost:8000/api/v1/generate-loom-file-async', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        design_id: 'temp-123',
        hooks: hooks,
        kali_count: kalis,
        picks_height: 8000
      })
    });
    const data = await res.json();
    if (data.task_id) {
      setTaskId(data.task_id);
    }
  };

  return (
    <header className="h-16 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-50 absolute top-0">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-slate-200">SJ<span className="text-[#38bdf8]">DAS</span> Studio</h1>
        <div className="h-6 w-px bg-slate-700 mx-2" />
        <span className="text-sm text-slate-400 font-mono">ID: temp-123</span>
      </div>

      <div className="flex items-center gap-6">
        {/* Mechanical Controls */}
        <div className="flex items-center gap-3 text-sm">
          <label className="text-slate-400">Hooks:</label>
          <input 
            type="number" 
            value={hooks}
            onChange={(e) => setMechanicalSpecs(Number(e.target.value), kalis)}
            className="w-20 bg-slate-800 border-slate-700 text-slate-200 rounded px-2 py-1 outline-none focus:border-[#38bdf8] transition-colors"
          />
        </div>
        <div className="flex items-center gap-3 text-sm">
          <label className="text-slate-400">Kalis:</label>
          <input 
            type="number" 
            value={kalis}
            onChange={(e) => setMechanicalSpecs(hooks, Number(e.target.value))}
            className="w-16 bg-slate-800 border-slate-700 text-slate-200 rounded px-2 py-1 outline-none focus:border-[#38bdf8] transition-colors"
          />
        </div>

        {/* Action Button */}
        <button 
          onClick={handleRunMachine}
          className="flex items-center gap-2 bg-[#38bdf8]/10 hover:bg-[#38bdf8]/20 border border-[#38bdf8]/50 text-[#38bdf8] px-4 py-2 rounded-md font-medium transition-all shadow-[0_0_15px_rgba(56,189,248,0.2)] hover:shadow-[0_0_20px_rgba(56,189,248,0.4)]"
        >
          <Play size={16} fill="currentColor" />
          Generate Loom File
        </button>
      </div>
    </header>
  );
}

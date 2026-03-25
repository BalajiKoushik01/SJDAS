import { create } from 'zustand';

interface StudioState {
  hooks: number;
  kalis: number;
  activeTool: 'cursor' | 'ai-trace' | 'heal' | 'bucket';
  taskId: string | null;
  wsMessage: string;
  setMechanicalSpecs: (hooks: number, kalis: number) => void;
  setWsUpdate: (message: string) => void;
  setActiveTool: (tool: 'cursor' | 'ai-trace' | 'heal' | 'bucket') => void;
  setTaskId: (id: string | null) => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  hooks: 600,
  kalis: 12,
  activeTool: 'cursor',
  taskId: null,
  wsMessage: 'Idle',
  
  setMechanicalSpecs: (hooks, kalis) => set({ hooks, kalis }),
  
  setWsUpdate: (wsMessage) => set({ wsMessage }),
  
  setActiveTool: (tool) => set({ activeTool: tool }),
  
  setTaskId: (id) => set({ taskId: id })
}));

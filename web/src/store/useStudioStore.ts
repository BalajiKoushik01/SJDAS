import { create } from 'zustand';

// ─── Types ───────────────────────────────────────────────────────────────────

export type ToolId = 'cursor' | 'lasso' | 'magic-wand' | 'quick-select'
  | 'brush' | 'pencil' | 'eraser' | 'fill' | 'gradient' | 'clone-stamp'
  | 'healing' | 'eyedropper' | 'zoom' | 'hand'
  | 'ai-trace' | 'heal' | 'bucket' | 'mirror';

export type RepeatMode = 'none' | 'straight' | 'half-drop' | 'mirror' | 'brick' | 'toss';
export type SareeStyle = 'Kanjivaram' | 'Banarasi' | 'Pochampally' | 'Paithani' | 'Other';
export type LoomBrand = 'Stäubli JC5' | 'Stäubli JC6' | 'Bonas' | 'Grosse' | 'Udayravi' | 'Custom';

export interface Layer {
  id: string;
  name: string;
  type: 'raster' | 'vector' | 'adjustment';
  visible: boolean;
  locked: boolean;
  opacity: number;
  blendMode: 'normal' | 'multiply' | 'screen' | 'overlay' | 'soft-light';
  region?: 'body' | 'border' | 'pallu' | 'motif';
}

export interface YarnColor {
  id: string;
  hex: string;
  name: string;
  pantone?: string;
  isLocked: boolean;
}

export interface DecodeResult {
  styleLabel: SareeStyle;
  styleConfidence: number;
  svgUrl: string;
  layers: Layer[];
  colors: YarnColor[];
  motifs: Array<{ class: string; confidence: number; bbox: [number, number, number, number] }>;
  weaveMatrix?: string; // base64 numpy array
  floatCheckPassed: boolean;
  analysisCard: string;
  weaveRecommendation: string;
  alert?: string;
}

export interface LoomStatus {
  id: string;
  name: string;
  brand: LoomBrand;
  ipAddress?: string;
  status: 'running' | 'idle' | 'error' | 'maintenance';
  currentDesign?: string;
  progress?: number; // 0-100
  errorCode?: string;
  errorMessage?: string;
  picksPerMinute?: number;
}

export interface AIAlert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  message: string;
  dismissible: boolean;
  actionLabel?: string;
  actionFn?: () => void;
}

// ─── State Interface ──────────────────────────────────────────────────────────

interface StudioState {
  // Mechanical
  hooks: number;
  kalis: number;
  loomBrand: LoomBrand;
  epi: number;  // ends per inch
  ppi: number;  // picks per inch

  // Studio
  activeTool: ToolId;
  activeLayerId: string | null;
  layers: Layer[];
  colorPalette: YarnColor[];
  repeatMode: RepeatMode;
  brushSize: number;
  brushOpacity: number;
  showGrid: boolean;
  showWeaveOverlay: boolean;
  zoomLevel: number;

  // Decode Pipeline
  uploadedFile: File | null;
  isDecoding: boolean;
  decodeProgress: number;       // 0-100
  decodeStepMessage: string;
  decodeResult: DecodeResult | null;
  colorCount: number;           // for decode color reduction
  styleOverride: SareeStyle | null;
  taskId: string | null;
  wsMessage: string;

  // AI
  aiAlerts: AIAlert[];
  aiChatOpen: boolean;

  // Factory Monitor
  looms: LoomStatus[];

  // Actions ──────────────────────────────────────────────────────────────────

  // Mechanical
  setMechanicalSpecs: (hooks: number, kalis: number) => void;
  setLoomParams: (params: Partial<Pick<StudioState, 'loomBrand' | 'epi' | 'ppi'>>) => void;

  // Studio
  setActiveTool: (tool: ToolId) => void;
  setActiveLayer: (id: string | null) => void;
  addLayer: (layer: Layer) => void;
  updateLayer: (id: string, patch: Partial<Layer>) => void;
  removeLayer: (id: string) => void;
  reorderLayers: (layers: Layer[]) => void;
  setColorPalette: (colors: YarnColor[]) => void;
  addYarnColor: (color: YarnColor) => void;
  setRepeatMode: (mode: RepeatMode) => void;
  setBrushSize: (size: number) => void;
  setBrushOpacity: (opacity: number) => void;
  setShowGrid: (show: boolean) => void;
  setZoom: (zoom: number) => void;

  // Decode
  setUploadedFile: (file: File | null) => void;
  setDecodeProgress: (progress: number, message?: string) => void;
  setDecodeResult: (result: DecodeResult | null) => void;
  setColorCount: (count: number) => void;
  setStyleOverride: (style: SareeStyle | null) => void;
  setTaskId: (id: string | null) => void;
  setWsUpdate: (message: string) => void;
  startDecoding: () => void;
  finishDecoding: () => void;

  // AI
  addAIAlert: (alert: AIAlert) => void;
  dismissAIAlert: (id: string) => void;
  setAIChatOpen: (open: boolean) => void;

  // Factory
  setLooms: (looms: LoomStatus[]) => void;
  updateLoom: (id: string, patch: Partial<LoomStatus>) => void;
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useStudioStore = create<StudioState>((set) => ({
  // Defaults
  hooks: 600,
  kalis: 12,
  loomBrand: 'Stäubli JC5',
  epi: 72,
  ppi: 80,

  activeTool: 'cursor',
  activeLayerId: null,
  layers: [],
  colorPalette: [],
  repeatMode: 'none',
  brushSize: 10,
  brushOpacity: 100,
  showGrid: false,
  showWeaveOverlay: false,
  zoomLevel: 100,

  uploadedFile: null,
  isDecoding: false,
  decodeProgress: 0,
  decodeStepMessage: 'Ready',
  decodeResult: null,
  colorCount: 6,
  styleOverride: null,
  taskId: null,
  wsMessage: 'Idle',

  aiAlerts: [],
  aiChatOpen: false,
  looms: [],

  // Mechanical
  setMechanicalSpecs: (hooks, kalis) => set({ hooks, kalis }),
  setLoomParams: (params) => set(params),

  // Studio
  setActiveTool: (tool) => set({ activeTool: tool }),
  setActiveLayer: (id) => set({ activeLayerId: id }),
  addLayer: (layer) => set((s) => ({ layers: [layer, ...s.layers] })),
  updateLayer: (id, patch) => set((s) => ({
    layers: s.layers.map((l) => (l.id === id ? { ...l, ...patch } : l))
  })),
  removeLayer: (id) => set((s) => ({ layers: s.layers.filter((l) => l.id !== id) })),
  reorderLayers: (layers) => set({ layers }),
  setColorPalette: (colorPalette) => set({ colorPalette }),
  addYarnColor: (color) => set((s) => ({ colorPalette: [...s.colorPalette, color] })),
  setRepeatMode: (repeatMode) => set({ repeatMode }),
  setBrushSize: (brushSize) => set({ brushSize }),
  setBrushOpacity: (brushOpacity) => set({ brushOpacity }),
  setShowGrid: (showGrid) => set({ showGrid }),
  setZoom: (zoomLevel) => set({ zoomLevel }),

  // Decode
  setUploadedFile: (uploadedFile) => set({ uploadedFile }),
  setDecodeProgress: (decodeProgress, message) => set({
    decodeProgress,
    ...(message ? { decodeStepMessage: message } : {})
  }),
  setDecodeResult: (decodeResult) => set({ decodeResult }),
  setColorCount: (colorCount) => set({ colorCount }),
  setStyleOverride: (styleOverride) => set({ styleOverride }),
  setTaskId: (taskId) => set({ taskId }),
  setWsUpdate: (wsMessage) => set({ wsMessage }),
  startDecoding: () => set({ isDecoding: true, decodeProgress: 0, decodeResult: null }),
  finishDecoding: () => set({ isDecoding: false }),

  // AI
  addAIAlert: (alert) => set((s) => ({ aiAlerts: [alert, ...s.aiAlerts] })),
  dismissAIAlert: (id) => set((s) => ({ aiAlerts: s.aiAlerts.filter((a) => a.id !== id) })),
  setAIChatOpen: (aiChatOpen) => set({ aiChatOpen }),

  // Factory
  setLooms: (looms) => set({ looms }),
  updateLoom: (id, patch) => set((s) => ({
    looms: s.looms.map((l) => (l.id === id ? { ...l, ...patch } : l))
  })),
}));

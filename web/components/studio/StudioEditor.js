'use client';

import { useState, useRef } from 'react';
import {
    MousePointer2, Hand, Type, Square, Image as ImageIcon,
    Layers, Eye, Lock, MoreHorizontal, Settings, ZoomIn, ZoomOut,
    Move, Download
} from "lucide-react";
import { motion } from "framer-motion";
import Image from 'next/image';

// ... imports
import { API } from '@/lib/api';

export default function StudioEditor() {
    // --- State ---
    const [activeTool, setActiveTool] = useState('select');
    const [zoom, setZoom] = useState(100);
    const [layers, setLayers] = useState([
        { id: '1', name: 'Pattern Overlay', type: 'image', visible: true, locked: false },
        { id: '2', name: 'Base Fabric', type: 'fill', visible: true, locked: true },
    ]);
    const [selectedLayer, setSelectedLayer] = useState('1');

    // Generation State
    const [loading, setLoading] = useState(false);
    const [generatedImage, setGeneratedImage] = useState(null);
    const [genParams, setGenParams] = useState({
        design_type: 'border',
        style: 'traditional',
        motifs: ['peacock'],
        complexity: 'medium'
    });

    // --- Actions ---
    const handleGenerate = async () => {
        setLoading(true);
        try {
            const result = await API.generateTexture("Generate", genParams, 'procedural');
            if (result?.url) {
                setGeneratedImage(result.url);
                // Also add as a layer
                setLayers(prev => [{ id: Date.now().toString(), name: 'Generated Result', type: 'image', visible: true, locked: false }, ...prev]);
            }
        } catch (e) {
            alert("Generation Failed: Check Backend Connection");
        } finally {
            setLoading(false);
        }
    };

    // --- Tools ---
    const tools = [
        { id: 'select', icon: MousePointer2, label: 'Move (V)' },
        { id: 'hand', icon: Hand, label: 'Pan (H)' },
        { id: 'shape', icon: Square, label: 'Shape (U)' },
        { id: 'text', icon: Type, label: 'Text (T)' },
        { id: 'image', icon: ImageIcon, label: 'Place Image' },
    ];

    return (
        <div className="flex h-full w-full bg-[#1e1e1e] text-white overflow-hidden relative">

            {/* 1. Left Toolbar */}
            <div className="w-12 bg-[#2c2c2e] border-r border-[#3a3a3c] flex flex-col items-center py-4 gap-4 z-30">
                {tools.map(tool => (
                    <button
                        key={tool.id}
                        onClick={() => setActiveTool(tool.id)}
                        className={`p-2 rounded-[6px] transition-all ${activeTool === tool.id ? 'bg-blue-600 text-white shadow-sm' : 'text-[#888] hover:bg-[#3a3a3c] hover:text-[#eee]'}`}
                        title={tool.label}
                    >
                        <tool.icon size={18} />
                    </button>
                ))}
            </div>

            {/* 2. Main Canvas Area */}
            <div className="flex-1 bg-[#121212] relative overflow-hidden cursor-crosshair flex items-center justify-center">
                {/* Infinite Grid Background */}
                <div className="absolute inset-0 opacity-[0.05]"
                    style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '24px 24px' }}
                />

                {/* Canvas Stage */}
                <motion.div
                    className="w-[800px] h-[600px] bg-white shadow-2xl relative overflow-hidden"
                    animate={{ scale: zoom / 100 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                    {/* Canvas Content */}
                    {generatedImage ? (
                        <div className="relative w-full h-full">
                            <Image src={generatedImage} fill unoptimized className="object-contain" alt="Generated Design" />
                        </div>
                    ) : (
                        <div className="absolute inset-0 bg-neutral-100 flex items-center justify-center text-black/20 font-bold text-4xl select-none">
                            Canvas {800}x{600}
                        </div>
                    )}
                </motion.div>

                {/* Floating Zoom Controls */}
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-[#2c2c2e] border border-[#3a3a3c] rounded-full px-4 py-2 flex items-center gap-4 shadow-xl z-20">
                    <button onClick={() => setZoom(z => Math.max(10, z - 10))} className="text-[#eee] hover:text-white"><ZoomOut size={16} /></button>
                    <span className="text-xs font-mono font-medium w-12 text-center">{zoom}%</span>
                    <button onClick={() => setZoom(z => Math.min(200, z + 10))} className="text-[#eee] hover:text-white"><ZoomIn size={16} /></button>
                </div>
            </div>

            {/* 3. Right Property/Layers Panel */}
            <div className="w-[280px] bg-[#1e1e1e] border-l border-[#3a3a3c] flex flex-col z-30">

                {/* Properties Header */}
                <div className="h-[52px] border-b border-[#3a3a3c] flex items-center px-4 justify-between bg-[#2c2c2e]">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#aaa]">Properties</span>
                    <Settings size={14} className="text-[#888]" />
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6">

                    {/* Generators */}
                    <div className="space-y-3">
                        <Label>AI Generation</Label>
                        <button
                            onClick={handleGenerate}
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-medium py-2 rounded-[6px] text-xs shadow-md transition-all flex items-center justify-center gap-2"
                        >
                            {loading ? <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Generate Design'}
                        </button>
                    </div>

                    <div className="h-[1px] bg-[#333]" />

                    {/* Transform */}
                    <div className="space-y-3">
                        <Label>Transform</Label>
                        <div className="grid grid-cols-2 gap-2">
                            <Input label="X" value="0" />
                            <Input label="Y" value="0" />
                            <Input label="W" value="800" />
                            <Input label="H" value="600" />
                        </div>
                    </div>


                    {/* Layers Panel */}
                    <div className="space-y-3 pt-4 border-t border-[#333]">
                        <div className="flex items-center justify-between">
                            <Label>Layers</Label>
                            <button className="text-[#888] hover:text-white"><MoreHorizontal size={14} /></button>
                        </div>

                        <div className="space-y-1">
                            {layers.map(layer => (
                                <div
                                    key={layer.id}
                                    onClick={() => setSelectedLayer(layer.id)}
                                    className={`flex items-center gap-3 p-2 rounded-[6px] border ${selectedLayer === layer.id ? 'bg-[#007AFF]/20 border-[#007AFF]/50' : 'bg-[#2c2c2e] border-[#3a3a3c] hover:border-[#555]'} cursor-pointer group transtion-all`}
                                >
                                    <button className="text-[#666] group-hover:text-[#aaa]">
                                        {layer.visible ? <Eye size={14} /> : <Eye size={14} className="opacity-30" />}
                                    </button>
                                    <span className="text-[12px] flex-1 truncate">{layer.name}</span>
                                    {layer.locked && <Lock size={12} className="text-[#555]" />}
                                </div>
                            ))}
                        </div>
                    </div>

                </div>
            </div>

        </div>
    );
}

// --- Subcomponents ---

const Label = ({ children }) => (
    <div className="text-[10px] font-bold text-[#666] uppercase tracking-wider mb-1">{children}</div>
);

const Input = ({ label, value }) => (
    <div className="flex items-center bg-[#121212] border border-[#333] rounded-[4px] px-2 py-1">
        <span className="text-[10px] text-[#555] mr-2 w-2">{label}</span>
        <input className="bg-transparent text-[11px] outline-none w-full font-mono text-[#ccc]" defaultValue={value} />
    </div>
);

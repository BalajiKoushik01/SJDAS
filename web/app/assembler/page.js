'use client';

import { useState } from 'react';
import { Layers, Plus, Upload } from "lucide-react";

export default function AssemblerPage() {
    const [layers, setLayers] = useState([
        { id: 1, name: 'Base Silk_001', type: 'base', visible: true },
        { id: 2, name: 'Zari Border_Gold', type: 'border', visible: true },
        { id: 3, name: 'Pallu_Peacock', type: 'pallu', visible: true }
    ]);

    return (
        <div className="h-full flex text-white select-none">
            {/* Layers Panel */}
            <div className="mac-sidebar w-[280px] p-4 flex flex-col shrink-0 z-20">
                <h2 className="text-[11px] font-bold text-[#666] uppercase tracking-wider mb-4">Composition Layers</h2>

                <div className="flex-1 space-y-2 overflow-y-auto">
                    {layers.map(layer => (
                        <div key={layer.id} className="bg-[#2c2c2e] p-3 rounded-[8px] flex items-center justify-between border border-[var(--system-gray-5)] group hover:border-[#444]">
                            <div className="flex items-center gap-3">
                                <Layers size={14} className="text-[#888]" />
                                <span className="text-[13px] font-medium">{layer.name}</span>
                            </div>
                            <div className="w-2 h-2 rounded-full bg-green-500 shadow-sm" />
                        </div>
                    ))}

                    <button className="w-full py-2 border border-dashed border-[#444] rounded-[8px] text-[#666] text-[12px] flex items-center justify-center gap-2 hover:bg-[#2c2c2e] hover:text-white transition-colors">
                        <Plus size={14} /> Add Layer
                    </button>
                </div>

                <div className="pt-4 border-t border-[#333]">
                    <button className="mac-button w-full flex items-center justify-center gap-2">
                        Export Composite
                    </button>
                </div>
            </div>

            {/* Canvas */}
            <div className="flex-1 bg-[#121212] relative flex items-center justify-center">
                {/* Checkerboard Background for Transparency */}
                <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(45deg, #333 25%, transparent 25%), linear-gradient(-45deg, #333 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #333 75%), linear-gradient(-45deg, transparent 75%, #333 75%)`, backgroundSize: '20px 20px', backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px' }} />

                <div className="w-[60%] aspect-[4/5] bg-black shadow-2xl border border-[#333] relative overflow-hidden flex items-center justify-center">
                    <p className="text-[#333] font-medium text-sm">Preview Render</p>
                    {/* Placeholder for Canvas */}
                </div>
            </div>
        </div>
    );
}

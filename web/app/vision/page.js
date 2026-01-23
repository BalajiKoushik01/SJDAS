'use client';

import { useState } from 'react';
import { Scan, Upload, FileText, CheckCircle } from "lucide-react";
import { API } from '@/lib/api';

export default function VisionPage() {
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);

    const handleUpload = () => {
        setAnalyzing(true);
        setTimeout(async () => {
            const res = await API.analyzePattern(null);
            setResult(res);
            setAnalyzing(false);
        }, 3000); // Simulate processing time
    };

    return (
        <div className="h-full flex flex-col items-center justify-center p-8 relative">

            {!result ? (
                <div className="max-w-md w-full text-center space-y-8">
                    <div className="w-24 h-24 bg-[#1c1c1e] rounded-[24px] border border-[#333] mx-auto flex items-center justify-center shadow-2xl relative">
                        {analyzing && <div className="absolute inset-0 rounded-[24px] border-2 border-blue-500 animate-pulse" />}
                        <Scan size={40} className={`text-white ${analyzing ? 'animate-spin' : ''}`} />
                    </div>

                    <div>
                        <h1 className="text-2xl font-bold text-white mb-2">Vision Analysis</h1>
                        <p className="text-[#888]">Upload a saree pattern to deconstruct its motifs and weave style.</p>
                    </div>

                    <div
                        onClick={!analyzing ? handleUpload : null}
                        className={`h-40 border-2 border-dashed rounded-[16px] flex flex-col items-center justify-center gap-4 transition-all cursor-pointer ${analyzing ? 'border-blue-500/30 bg-blue-500/5' : 'border-[#333] hover:border-[#666] hover:bg-[#1c1c1e]'}`}
                    >
                        {analyzing ? (
                            <span className="text-blue-400 text-sm font-medium">Processing Neural Network...</span>
                        ) : (
                            <>
                                <Upload size={24} className="text-[#666]" />
                                <span className="text-[#666] text-sm">Drop image here or click to browse</span>
                            </>
                        )}
                    </div>
                </div>
            ) : (
                <div className="max-w-4xl w-full grid grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <div className="aspect-square bg-[#1c1c1e] rounded-[16px] border border-[#333] overflow-hidden">
                        {/* Mock Image Display */}
                        <div className="w-full h-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center text-[#444]">
                            Source Image
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <h2 className="text-xl font-semibold text-white mb-1">Analysis Complete</h2>
                            <p className="text-[#666] text-sm">Confidence Score: 98.4%</p>
                        </div>

                        <div className="space-y-4">
                            <div className="bg-[#1c1c1e] p-4 rounded-[12px] border border-[#333]">
                                <label className="text-xs text-[#666] uppercase tracking-wider block mb-2">Detected Motifs</label>
                                <div className="flex gap-2">
                                    {result.motifs.map(m => (
                                        <span key={m} className="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full text-xs font-medium capitalize">
                                            {m}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-[#1c1c1e] p-4 rounded-[12px] border border-[#333]">
                                <label className="text-xs text-[#666] uppercase tracking-wider block mb-2">Historical Era</label>
                                <div className="flex items-center gap-2 text-white font-medium">
                                    <FileText size={16} className="text-[#888]" />
                                    {result.era}
                                </div>
                            </div>
                        </div>

                        <button onClick={() => setResult(null)} className="mac-button w-full py-2">Analyze Another</button>
                    </div>
                </div>
            )}

        </div>
    );
}

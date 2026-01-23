'use client';

import { useState, useEffect } from 'react';
import { Cpu, Activity, Terminal, CheckCircle } from "lucide-react";
import { API } from '@/lib/api';

export default function JulesPage() {
    const [status, setStatus] = useState(null);
    const [logs, setLogs] = useState([
        "[JULES] System Initialized...",
        "[JULES] Monitoring Backend Status: OK",
        "[JULES] GPU Resources: Idle"
    ]);

    useEffect(() => {
        // Poll for status
        const fetchStatus = async () => {
            const s = await API.getJulesStatus();
            setStatus(s);
        };
        fetchStatus();
    }, []);

    return (
        <div className="h-full flex flex-col bg-[#000] text-white">
            <header className="h-16 border-b border-[#333] flex items-center px-8 justify-between shrink-0 bg-[#111]">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-emerald-500/10 rounded-full flex items-center justify-center border border-emerald-500/20">
                        <Cpu size={20} className="text-emerald-500" />
                    </div>
                    <div>
                        <h1 className="font-semibold">Jules Maintenance Engine</h1>
                        <p className="text-xs text-[#666]">Autonomous System Agent v2.0</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 px-3 py-1 bg-[#222] rounded-full border border-[#333]">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-medium text-emerald-500">Active</span>
                </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
                {/* Metrics */}
                <div className="w-[300px] border-r border-[#333] bg-[#111] p-6 space-y-6">
                    <div>
                        <h3 className="text-xs font-bold text-[#666] uppercase tracking-wider mb-4">Core Metrics</h3>
                        <div className="space-y-4">
                            <div className="p-4 rounded-[12px] bg-[#1c1c1e] border border-[#333]">
                                <div className="flex items-center gap-2 mb-2 text-[#888] text-xs">
                                    <Activity size={14} /> System Uptime
                                </div>
                                <div className="text-2xl font-mono">{status?.uptime || "--:--"}</div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-xs font-bold text-[#666] uppercase tracking-wider mb-4">Active Tasks</h3>
                        <div className="space-y-2">
                            {status?.tasks?.map(task => (
                                <div key={task.id} className="flex items-center justify-between text-sm p-2 rounded-[6px] hover:bg-[#222]">
                                    <span className="text-[#ccc]">{task.name}</span>
                                    {task.status === 'completed' ? <CheckCircle size={14} className="text-emerald-500" /> : <div className="w-3 h-3 border-2 border-[#666] border-t-transparent rounded-full animate-spin" />}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Terminal */}
                <div className="flex-1 bg-[#000] p-6 font-mono text-sm relative">
                    <div className="absolute top-4 right-4 opacity-20">
                        <Terminal size={120} />
                    </div>

                    <div className="space-y-2 relative z-10">
                        {logs.map((log, i) => (
                            <div key={i} className="text-[#0f0] opacity-80 border-l-2 border-[#0f0] pl-3">
                                {log}
                            </div>
                        ))}
                        <div className="w-2 h-4 bg-[#0f0] animate-pulse" />
                    </div>
                </div>
            </div>
        </div>
    );
}

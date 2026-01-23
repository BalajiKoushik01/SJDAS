'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Palette, Layers, Cpu, Scan, Settings } from "lucide-react";
import MotionWrapper from "@/components/ui/MotionWrapper";
import CustomCursor from "@/components/ui/CustomCursor";

/* Nav Item Component */
function NavItem({ href, icon: Icon, label }) {
    const pathname = usePathname();
    const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));

    return (
        <Link href={href}>
            <div className={`relative w-10 h-10 flex items-center justify-center rounded-[10px] transition-all duration-200 group ${isActive ? 'bg-[var(--system-blue)] text-white shadow-md' : 'text-[var(--system-gray)] hover:bg-[var(--system-gray-5)] hover:text-white'}`}>
                <Icon strokeWidth={2} size={20} />

                {/* Tooltip */}
                <span className="absolute left-14 bg-[var(--system-gray-6)] text-white text-[11px] font-medium px-2 py-1 rounded-[4px] border border-[var(--system-gray-5)] opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all pointer-events-none whitespace-nowrap z-50 shadow-xl">
                    {label}
                </span>
            </div>
        </Link>
    );
}

export default function AppShell({ children }) {
    return (
        <div className="flex h-screen overflow-hidden bg-black text-white selection:bg-blue-500/30">
            <CustomCursor />

            {/* Global Navigation Rail */}
            <nav className="w-[60px] bg-[#1a1a1a] border-r border-[var(--system-gray-5)] flex flex-col items-center py-4 z-50 shrink-0">
                <div className="mb-6">
                    <div className="w-8 h-8 rounded-[8px] bg-gradient-to-br from-white to-[#999] flex items-center justify-center shadow-lg">
                        <span className="text-black font-bold text-xs">SJ</span>
                    </div>
                </div>

                <div className="flex-1 flex flex-col gap-3 w-full items-center">
                    <NavItem href="/" icon={Home} label="Launcher" />
                    <div className="w-8 h-[1px] bg-[var(--system-gray-5)] my-1" />
                    <NavItem href="/studio" icon={Palette} label="Studio" />
                    <NavItem href="/assembler" icon={Layers} label="Assembler" />
                    <NavItem href="/vision" icon={Scan} label="Vision" />
                    <div className="flex-1" />
                    <NavItem href="/jules" icon={Cpu} label="Jules (Auto)" />
                    <NavItem href="#" icon={Settings} label="Settings" />
                </div>
            </nav>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col min-w-0 bg-[var(--system-background)] relative overflow-hidden">
                {/* Shared Background Effects */}
                <div className="fixed inset-0 pointer-events-none z-[0] opacity-[0.03] mix-blend-overlay">
                    <svg width="100%" height="100%"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.80" numOctaves="4" stitchTiles="stitch" /></filter><rect width="100%" height="100%" filter="url(#noise)" /></svg>
                </div>

                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[120px] rounded-full pointer-events-none mix-blend-screen z-[1]" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[120px] rounded-full pointer-events-none mix-blend-screen z-[1]" />

                <div className="relative z-[10] h-full w-full">
                    <MotionWrapper>
                        {children}
                    </MotionWrapper>
                </div>
            </main>
        </div>
    );
}

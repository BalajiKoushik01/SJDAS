'use client';

import React from 'react';
import { Palette, Layers, Cpu, Scan } from "lucide-react";
import { motion } from "framer-motion";
import SpotlightCard from '@/components/ui/SpotlightCard';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function Home() {
  const apps = [
    {
      title: "Design Studio",
      description: "Neural Textile Generation",
      icon: <Palette className="w-8 h-8 text-white" />,
      href: "/studio",
      color: "bg-blue-600"
    },
    {
      title: "Assembler",
      description: "Composition Timeline",
      icon: <Layers className="w-8 h-8 text-white" />,
      href: "/assembler",
      color: "bg-purple-600"
    },
    {
      title: "Jules Engine",
      description: "System Maintenance",
      icon: <Cpu className="w-8 h-8 text-white" />,
      href: "#",
      color: "bg-emerald-600"
    },
    {
      title: "Vision",
      description: "Pattern Analysis",
      icon: <Scan className="w-8 h-8 text-white" />,
      href: "/vision",
      color: "bg-orange-600"
    }
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center font-sans relative z-10">

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="mb-12 text-center"
      >
        <span className="inline-block mb-4 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] uppercase tracking-widest text-[var(--system-gray)] backdrop-blur-md">
          SJ-DAS Professional v2026
        </span>
        <h1 className="text-4xl font-semibold tracking-tight text-white mb-2 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
          Welcome Home
        </h1>
        <p className="text-[var(--system-gray)] text-sm max-w-md mx-auto">
          Select a workspace to begin your creative session.
        </p>
      </motion.div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl w-full px-6"
      >
        {apps.map((app, i) => (
          <motion.div key={i} variants={item} className="h-full">
            <SpotlightCard href={app.href} className="p-6 h-full flex flex-col items-center text-center backdrop-blur-xl bg-black/40 border-white/5 hover:border-white/20 transition-colors">
              <div className={`w-14 h-14 ${app.color} rounded-[16px] flex items-center justify-center mb-4 shadow-[0_8px_16px_rgba(0,0,0,0.5)] group-hover:scale-110 transition-transform duration-500`}>
                {app.icon}
              </div>
              <h3 className="font-medium text-white mb-1">{app.title}</h3>
              <p className="text-xs text-[var(--system-gray)]">{app.description}</p>
            </SpotlightCard>
          </motion.div>
        ))}
      </motion.div>

      <footer className="mt-24 text-[var(--system-gray)] text-[10px] tracking-widest uppercase opacity-40">
        System Operational
      </footer>
    </main>
  );
}

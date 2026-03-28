'use client';

import { useEffect, useRef } from 'react';
import * as fabric from 'fabric';
import { useStudioStore } from '@/store/useStudioStore';

export default function FabricWorkspace() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const hooks = useStudioStore((state) => state.hooks);
  const activeTool = useStudioStore((state) => state.activeTool);
  
  // Rule: We isolate the fabric instance in a Ref to avoid React re-renders crushing performance
  const fabricRef = useRef<fabric.Canvas | null>(null);

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return;
    
    // Initialize Fabric
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
      backgroundColor: '#1e293b', // Tailwind slate-800
      selection: true,
      preserveObjectStacking: true,
    });
    
    fabricRef.current = canvas;

    // The Grid Snapping Logic
    // Fabric 7.x approach to drawing backgrounds/grids manually or tracking object movements
    canvas.on('object:moving', (e) => {
        if (!e.target) return;
        const target = e.target;
        
        // Simulating physical Hook Constraints
        // E.g., if hook distance = 10px in the UI view
        const snapSize = 10; 
        
        if (target.left !== undefined) {
             target.set({ left: Math.round(target.left / snapSize) * snapSize });
        }
        if (target.top !== undefined) {
             target.set({ top: Math.round(target.top / snapSize) * snapSize });
        }
    });

    // Infinite Panning (Space + Drag logic)
    canvas.on('mouse:down', function (opt) {
      const evt = opt.e as MouseEvent;
      if (evt.altKey === true) { // Alt or Space implementation
        (canvas as any).isDragging = true;
        canvas.selection = false;
        (canvas as any).lastPosX = evt.clientX;
        (canvas as any).lastPosY = evt.clientY;
      }
    });
    
    canvas.on('mouse:move', function (opt) {
      if ((canvas as any).isDragging) {
        const e = opt.e as MouseEvent;
        if (!canvas.viewportTransform) return;
        const vpt = canvas.viewportTransform;
        vpt[4] += e.clientX - (canvas as any).lastPosX;
        vpt[5] += e.clientY - (canvas as any).lastPosY;
        canvas.requestRenderAll();
        (canvas as any).lastPosX = e.clientX;
        (canvas as any).lastPosY = e.clientY;
      }
    });
    
    canvas.on('mouse:up', function () {
      canvas.setViewportTransform(canvas.viewportTransform!);
      (canvas as any).isDragging = false;
      canvas.selection = true;
    });

    // Cleanup
    return () => {
      canvas.dispose();
      fabricRef.current = null;
    };
  }, []);

  // Sync mechanical constraints silently without breaking canvas
  useEffect(() => {
     if (!fabricRef.current) return;
     // Adjust UI bounds based on Hooks changing
     console.log("Hooks changed to:", hooks);
  }, [hooks]);

  return (
    <div ref={containerRef} className="w-full h-full relative bg-slate-900 overflow-hidden cursor-crosshair">
      <canvas ref={canvasRef} className="absolute inset-0" />
      {/* Heatmap Overlay for Float Checking will sit here via z-index */}
    </div>
  );
}

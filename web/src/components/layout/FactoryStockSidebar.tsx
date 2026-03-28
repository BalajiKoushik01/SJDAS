'use client';

import { Activity, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiV1 } from '@/lib/runtime';
import { useStudioStore } from '@/store/useStudioStore';

export default function FactoryStockSidebar() {
  const { colorPalette, setColorPalette } = useStudioStore();
  const [inventory, setInventory] = useState([
    { id: 1, name: 'Deep Cobalt Silk', hex: '#000080', kg: 45.0, status: 'ok' },
    { id: 2, name: 'Gold Zari 200D', hex: '#FFD700', kg: 1.2, status: 'low' },
    { id: 3, name: 'Silver Border Zari', hex: '#C0C0C0', kg: 12.5, status: 'ok' }
  ]);
  const [isSyncing, setIsSyncing] = useState(false);

  // Fetch real inventory from backend on mount
  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const response = await apiV1('/factory/inventory');
        if (response && response.items) {
          setInventory(response.items);
        }
      } catch (err) {
        console.error('Failed to fetch factory inventory:', err);
      }
    };
    fetchInventory();
  }, []);

  const handleSnapToStock = async () => {
    setIsSyncing(true);
    try {
      const designColors = colorPalette.map(c => c.hex);
      const response = await apiV1('/factory/match-stock', {
        method: 'POST',
        body: JSON.stringify({
           design_colors: designColors,
           factory_id: 'LOC_DEFAULT'
        })
      });

      if (response && response.matches) {
        // Update the studio store with the matched physical colors
        const updatedPalette = colorPalette.map((color, idx) => {
          const match = response.matches.find((m: any) => m.requested_color === color.hex);
          if (match) {
            return { ...color, hex: match.hex, name: match.thread_name };
          }
          return color;
        });
        setColorPalette(updatedPalette);
      }
    } catch (err) {
      console.error('Snap to stock failed:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="w-80 h-full border-l border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col z-40 float-right pt-16">
      <div className="p-5 border-b border-slate-800/50 flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-wider text-slate-300 uppercase flex items-center gap-2">
          <Activity size={16} className="text-[#38bdf8]" />
          Factory Limits
        </h2>
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        <p className="text-xs text-slate-500 mb-4 font-mono">
          Real-time Delta-E calculations binding vectors to physical stock.
        </p>
        
        <div className="flex flex-col gap-3">
          {inventory.map((item) => (
            <div key={item.id} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50 relative overflow-hidden group">
              {/* Colored left accent */}
              <div 
                className="absolute left-0 top-0 bottom-0 w-1.5" 
                style={{ backgroundColor: item.hex }} 
              />
              
              <div className="flex justify-between items-start pl-2">
                <div>
                  <h3 className="text-sm font-medium text-slate-200">{item.name}</h3>
                  <p className="text-xs text-slate-500 mt-1">{item.kg} kg in stock</p>
                </div>
                
                {/* Traffic Light Dot */}
                <div className="flex items-center justify-center p-1 rounded-full bg-slate-900 border border-slate-700">
                  <div className={`w-2.5 h-2.5 rounded-full ${item.status === 'ok' ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]'}`} />
                </div>
              </div>
            </div>
          ))}
        </div>

        <button 
          onClick={handleSnapToStock}
          disabled={isSyncing}
          className="w-full mt-6 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 py-2.5 rounded-md text-sm transition-colors shadow-lg flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isSyncing ? <RefreshCw size={14} className="animate-spin" /> : null}
          {isSyncing ? 'Syncing...' : 'Snap Vectors to Stock'}
        </button>
      </div>
    </div>
  );
}

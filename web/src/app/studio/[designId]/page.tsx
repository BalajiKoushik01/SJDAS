import StudioHeader from '@/components/layout/StudioHeader';
import GlassToolbox from '@/components/tools/GlassToolbox';
import FactoryStockSidebar from '@/components/layout/FactoryStockSidebar';
import AgenticProgressModal from '@/components/feedback/AgenticProgressModal';
import dynamic from 'next/dynamic';

// Fabric strictly relies on browser globals (window/document), so it MUST be dynamically imported with ssr: false
const FabricWorkspace = dynamic(() => import('@/components/canvas/FabricWorkspace'), { ssr: false });

// We implement strict component separation here to keep the Fabric workspace
// pristine and completely isolated from standard React lifecycle hooks.
export default function StudioPage({ params }: { params: { designId: string } }) {
  return (
    <div className="w-screen h-screen overflow-hidden bg-[#0f172a] text-slate-200 flex flex-col relative">
      <StudioHeader />
      
      {/* The main workspace pushes down below the Absolute Header */}
      <main className="flex-1 w-full h-full relative pt-16 flex">
        
        {/* Left: The Glass Toolbox will float here */}
        <GlassToolbox />
        
        {/* Center: The Shadow Workspace (Fabric.js + Canvas) */}
        <div className="flex-1 h-full w-full relative bg-slate-900 border-2 border-slate-900">
           <FabricWorkspace />
        </div>

        {/* Right: The Factory Stock Sidebar */}
        <FactoryStockSidebar />

      </main>

      {/* The floating modal that triggers only when taskId exists */}
      <AgenticProgressModal />
    </div>
  );
}

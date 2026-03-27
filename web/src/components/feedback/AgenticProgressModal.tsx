'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStudioStore } from '@/store/useStudioStore';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { getWsBaseUrl } from '@/lib/runtime';

export default function AgenticProgressModal() {
  const taskId = useStudioStore((state) => state.taskId);
  const setTaskId = useStudioStore((state) => state.setTaskId);
  
  const [status, setStatus] = useState<'pending' | 'progress' | 'success' | 'error'>('pending');
  const [message, setMessage] = useState('Initializing AI Workers...');
  const [progress, setProgress] = useState(0);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;

    // Connect strictly to the FastAPI Celery stream
    const ws = new WebSocket(`${getWsBaseUrl()}/ws/progress/${taskId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      
      if (data.status === 'progress' && data.meta) {
        setMessage(data.meta.message || 'Processing...');
        setProgress(data.meta.progress || 0);
      } else if (data.status === 'success') {
        setMessage('Compilation Complete!');
        setFileUrl(data.file_url);
        setProgress(100);
      } else if (data.status === 'error') {
        setMessage(data.message || 'An error occurred during compilation.');
      }
    };

    return () => {
      ws.close();
    };
  }, [taskId]); // Re-run if taskId changes

  const handleClose = () => {
    setTaskId(null);
    setStatus('pending');
    setProgress(0);
    setMessage('Initializing AI Workers...');
    setFileUrl(null);
  };

  return (
    <AnimatePresence>
      {taskId && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm"
        >
          <motion.div 
            initial={{ scale: 0.95, y: 10 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 10 }}
            className="w-full max-w-md bg-slate-900 border border-slate-700 p-8 rounded-2xl shadow-2xl relative"
          >
            {/* Header */}
            <h2 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
              {status === 'pending' || status === 'progress' ? (
                 <Loader2 className="animate-spin text-[#38bdf8]" />
              ) : status === 'success' ? (
                 <CheckCircle2 className="text-emerald-400" />
              ) : (
                 <XCircle className="text-rose-500" />
              )}
              {status === 'success' ? 'Master File Ready' : 'AI Shadow Processing'}
            </h2>

            {/* Live WebSocket Text */}
            <p className="text-slate-400 font-mono text-sm mb-4 h-6">
              {message}
            </p>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-8">
              <motion.div 
                className={status === 'error' ? "h-full bg-rose-500" : "h-full bg-gradient-to-r from-cyan-500 to-[#38bdf8]"}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3 mt-4">
              {status === 'success' && fileUrl && (
                <a 
                  href={fileUrl}
                  download
                  className="bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/50 px-4 py-2 rounded-md font-medium transition-colors"
                >
                  Download .BMP File
                </a>
              )}
              
              <button 
                onClick={handleClose}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-md"
              >
                {status === 'success' || status === 'error' ? 'Close' : 'Cancel Process'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

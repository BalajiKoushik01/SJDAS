'use client';

import { useCallback, useState } from 'react';
import { useStudioStore } from '@/store/useStudioStore';
import { Upload, FileImage, X } from 'lucide-react';
import Image from 'next/image';

export default function UploadZone() {
  const setUploadedFile = useStudioStore((s) => s.setUploadedFile);
  const uploadedFile = useStudioStore((s) => s.uploadedFile);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback((file: File) => {
    if (!file.type.match(/^image\/(png|jpeg|webp)|application\/pdf/)) return;
    setUploadedFile(file);
    const url = URL.createObjectURL(file);
    setPreview(url);
  }, [setUploadedFile]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const clearFile = () => {
    setUploadedFile(null);
    setPreview(null);
  };

  return (
    <div>
      {!uploadedFile ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById('file-input')?.click()}
          style={{
            border: `2px dashed ${dragging ? 'var(--accent-gold)' : 'var(--border-hover)'}`,
            borderRadius: 'var(--radius-lg)',
            background: dragging ? 'var(--accent-gold-dim)' : 'var(--bg-hover)',
            padding: 48,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 200ms ease-out',
          }}
        >
          <Upload size={36} style={{ color: dragging ? 'var(--accent-gold)' : 'var(--text-muted)', margin: '0 auto 12px' }} />
          <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
            Drop your saree photo here
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
            PNG, JPG, WEBP, PDF • Any quality, any angle • Phone screenshot OK
          </div>
          <button className="btn-secondary">Browse Files</button>
          <input
            id="file-input" type="file" accept="image/png,image/jpeg,image/webp,application/pdf"
            style={{ display: 'none' }}
            onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
          />
        </div>
      ) : (
        <div style={{ borderRadius: 'var(--radius-lg)', overflow: 'hidden', position: 'relative' }}>
          {preview && (
            <div style={{ position: 'relative', width: '100%', height: 280, background: 'var(--bg-hover)', borderRadius: 'var(--radius-lg)' }}>
              <Image src={preview} alt="Preview" fill unoptimized style={{ objectFit: 'contain', borderRadius: 'var(--radius-lg)' }} />
            </div>
          )}
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', background: 'linear-gradient(transparent 50%, rgba(0,0,0,0.7))', borderRadius: 'var(--radius-lg)' }}>
            <div style={{ padding: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileImage size={16} style={{ color: 'var(--accent-gold)' }} />
                <span style={{ fontSize: 13, color: '#fff', fontWeight: 500 }}>{uploadedFile.name}</span>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.6)' }}>
                  {(uploadedFile.size / 1024 / 1024).toFixed(1)} MB
                </span>
              </div>
              <button
                onClick={clearFile}
                style={{ background: 'rgba(0,0,0,0.5)', border: 'none', borderRadius: '50%', width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#fff' }}
              >
                <X size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

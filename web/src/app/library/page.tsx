import Link from 'next/link';
import { Search, Filter, PlusCircle, ImageIcon } from 'lucide-react';

export default function LibraryPage() {
  return (
    <div style={{ padding: '32px', maxWidth: 1200 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Design Library</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4, fontSize: 13 }}>All your decoded and created designs, versioned and searchable.</p>
        </div>
        <Link href="/decode" style={{ textDecoration: 'none' }}>
          <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <PlusCircle size={14} /> New Decode
          </button>
        </Link>
      </div>

      {/* Search & Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="input" placeholder="Search by style, motif, color..." style={{ paddingLeft: 36 }} />
        </div>
        <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Filter size={14} /> Filter
        </button>
      </div>

      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['All', 'Kanjivaram', 'Banarasi', 'Pochampally', 'Loom-Ready', 'Draft'].map((f, i) => (
          <button key={f} style={{
            background: i === 0 ? 'var(--accent-gold-dim)' : 'transparent',
            color: i === 0 ? 'var(--accent-gold-light)' : 'var(--text-secondary)',
            border: `1px solid ${i === 0 ? 'rgba(201,168,76,0.3)' : 'var(--border-hover)'}`,
            borderRadius: 20, padding: '6px 14px', fontSize: 12, fontWeight: 500, cursor: 'pointer',
          }}>{f}</button>
        ))}
      </div>

      {/* Empty State */}
      <div className="card" style={{ textAlign: 'center', padding: 64 }}>
        <ImageIcon size={40} style={{ color: 'var(--text-muted)', margin: '0 auto 16px' }} />
        <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>No Designs Yet</div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 400, margin: '0 auto 24px' }}>
          Decode your first saree screenshot or create a design from scratch in the Studio.
        </div>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <Link href="/decode" style={{ textDecoration: 'none' }}>
            <button className="btn-primary">Decode Screenshot →</button>
          </Link>
          <Link href="/studio/new" style={{ textDecoration: 'none' }}>
            <button className="btn-secondary">Open Studio</button>
          </Link>
        </div>
      </div>
    </div>
  );
}

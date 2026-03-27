'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Search, Filter, PlusCircle, ImageIcon } from 'lucide-react';
import { apiV1 } from '@/lib/runtime';

export default function LibraryPage() {
  const [comments, setComments] = useState<Array<{ id: string; author: string; message: string }>>([]);
  const [snapshots, setSnapshots] = useState<Array<{ id: string; tag: string; created_by: string }>>([]);
  const designId = 'studio-active';

  useEffect(() => {
    const token = localStorage.getItem('sjdas_token') || '';
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.all([
      fetch(apiV1(`/premium/comments/${designId}`), { headers }).then((res) =>
        res.ok ? res.json() : { comments: [] },
      ),
      fetch(apiV1(`/premium/snapshots/${designId}`), { headers }).then((res) =>
        res.ok ? res.json() : { snapshots: [] },
      ),
    ]).then(([commentsRes, snapshotsRes]) => {
      setComments(Array.isArray(commentsRes.comments) ? commentsRes.comments : []);
      setSnapshots(Array.isArray(snapshotsRes.snapshots) ? snapshotsRes.snapshots : []);
    });
  }, []);

  const createApprovalRequest = async () => {
    const token = localStorage.getItem('sjdas_token') || '';
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    await fetch(apiV1('/premium/approvals/request'), {
      method: 'POST',
      headers,
      body: JSON.stringify({
        design_id: designId,
        requested_by: 'web-user',
        notes: 'Ready for loom export sign-off',
      }),
    });
    alert('Approval request submitted.');
  };

  const createSnapshot = async () => {
    const token = localStorage.getItem('sjdas_token') || '';
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    const response = await fetch(apiV1('/premium/snapshots'), {
      method: 'POST',
      headers,
      body: JSON.stringify({
        design_id: designId,
        tag: `v${snapshots.length + 1}`,
        created_by: 'web-user',
        metadata: { source: 'library-ui' },
      }),
    });
    if (response.ok) {
      const snapshot = await response.json();
      setSnapshots((current) => [snapshot, ...current]);
    }
  };

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
      <div className="card" style={{ textAlign: 'center', padding: 40 }}>
        <ImageIcon size={40} style={{ color: 'var(--text-muted)', margin: '0 auto 16px' }} />
        <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>Design Governance Workspace</div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 400, margin: '0 auto 24px' }}>
          Request export approvals, track review comments, and create version snapshots.
        </div>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button className="btn-primary" onClick={createApprovalRequest}>Request Approval</button>
          <button className="btn-secondary" onClick={createSnapshot}>Create Snapshot</button>
          <Link href="/decode" style={{ textDecoration: 'none' }}>
            <button className="btn-primary">Decode Screenshot →</button>
          </Link>
          <Link href="/studio/new" style={{ textDecoration: 'none' }}>
            <button className="btn-secondary">Open Studio</button>
          </Link>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Snapshots</h3>
          {snapshots.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No snapshots yet.</p>
          ) : (
            snapshots.map((snapshot) => (
              <div key={snapshot.id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <strong>{snapshot.tag}</strong> by {snapshot.created_by}
              </div>
            ))
          )}
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Comments</h3>
          {comments.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No comments yet.</p>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <strong>{comment.author}:</strong> {comment.message}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

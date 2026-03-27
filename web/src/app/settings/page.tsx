'use client';

import { useEffect, useState } from 'react';
import { apiV1 } from '@/lib/runtime';

type OrgUser = {
  id: string;
  username: string;
  role: string;
  active: boolean;
};

type AuditEvent = {
  id: string;
  event_type: string;
  actor: string;
  subject: string;
  details: string;
  timestamp: string;
};

export default function SettingsPage() {
  const [users, setUsers] = useState<OrgUser[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('sjdas_token') || '';
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.all([
      fetch(apiV1('/premium/users'), { headers }).then((res) => (res.ok ? res.json() : [])),
      fetch(apiV1('/premium/audit'), { headers }).then((res) => (res.ok ? res.json() : { events: [] })),
    ]).then(([usersResp, auditResp]) => {
      setUsers(Array.isArray(usersResp) ? usersResp : []);
      setAudit(Array.isArray(auditResp.events) ? auditResp.events : []);
    });
  }, []);

  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ margin: 0, fontSize: 24 }}>Enterprise Settings</h1>
      <p style={{ color: 'var(--text-secondary)' }}>
        Manage organization users, governance events, and auditability.
      </p>

      <div className="card" style={{ marginTop: 16, padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Organization Users</h2>
        {users.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No users loaded.</p>
        ) : (
          users.map((user) => (
            <div key={user.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span>{user.username}</span>
              <span style={{ color: 'var(--text-secondary)' }}>{user.role}</span>
            </div>
          ))
        )}
      </div>

      <div className="card" style={{ marginTop: 16, padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Audit Trail</h2>
        {audit.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No events yet.</p>
        ) : (
          audit.slice().reverse().slice(0, 12).map((event) => (
            <div key={event.id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{event.event_type}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                {event.actor} · {event.subject} · {event.details}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, ScanLine, ImageIcon, MonitorDot,
  BarChart3, Settings, ChevronLeft, ChevronRight,
  Cpu, User
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard',    href: '/',          icon: LayoutDashboard },
  { id: 'decode',    label: 'Decode',        href: '/decode',    icon: ScanLine,        badge: 'AI' },
  { id: 'studio',   label: 'Studio',        href: '/studio/new',icon: ImageIcon },
  { id: 'library',  label: 'Design Library',href: '/library',   icon: Cpu },
  { id: 'monitor',  label: 'Factory Monitor',href: '/monitor',  icon: MonitorDot },
  { id: 'analytics',label: 'Analytics',     href: '/analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings',      href: '/settings',  icon: Settings },
];

export default function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      style={{
        width: collapsed ? 64 : 220,
        transition: 'width 250ms cubic-bezier(0.4,0,0.2,1)',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        flexShrink: 0,
        overflow: 'hidden',
        zIndex: 40,
      }}
    >
      {/* Logo */}
      <div style={{
        height: 56, display: 'flex', alignItems: 'center',
        padding: collapsed ? '0 20px' : '0 16px',
        gap: 10, borderBottom: '1px solid var(--border)',
        justifyContent: collapsed ? 'center' : 'flex-start'
      }}>
        <div style={{
          width: 28, height: 28, borderRadius: 8,
          background: 'linear-gradient(135deg, var(--accent-gold), var(--accent-gold-light))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 13, fontWeight: 700, color: '#0a0b0f', flexShrink: 0,
        }}>SJ</div>
        {!collapsed && (
          <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>
            <span style={{ color: 'var(--accent-gold)' }}>SJ</span>DAS
          </span>
        )}
      </div>

      {/* Nav Items */}
      <nav style={{ flex: 1, padding: '12px 0', overflowY: 'auto' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.id}
              href={item.href}
              title={collapsed ? item.label : undefined}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: `10px ${collapsed ? '20px' : '12px'}`,
                margin: '1px 8px',
                borderRadius: 'var(--radius-sm)',
                textDecoration: 'none',
                color: isActive ? 'var(--accent-gold)' : 'var(--text-secondary)',
                background: isActive ? 'var(--accent-gold-dim)' : 'transparent',
                border: isActive ? '1px solid rgba(201,168,76,0.3)' : '1px solid transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: 13,
                transition: 'all 150ms ease-out',
                justifyContent: collapsed ? 'center' : 'flex-start',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.background = 'var(--bg-hover)';
                  (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.background = 'transparent';
                  (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
                }
              }}
            >
              <Icon size={16} style={{ flexShrink: 0 }} />
              {!collapsed && (
                <>
                  <span style={{ flex: 1 }}>{item.label}</span>
                  {item.badge && (
                    <span className="badge-purple" style={{ padding: '2px 6px', fontSize: 9 }}>
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Pill */}
      <div style={{
        borderTop: '1px solid var(--border)',
        padding: collapsed ? '12px 0' : '12px 8px',
      }}>
        {!collapsed ? (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 8px', borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-hover)',
          }}>
            <div style={{
              width: 30, height: 30, borderRadius: '50%',
              background: 'linear-gradient(135deg,#8b6ff5,#4fa3ff)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <User size={14} color="#fff" />
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.2 }}>
                SJDAS Workspace
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Enterprise Admin</div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div style={{
              width: 30, height: 30, borderRadius: '50%',
              background: 'linear-gradient(135deg,#8b6ff5,#4fa3ff)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <User size={14} color="#fff" />
            </div>
          </div>
        )}
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        style={{
          position: 'absolute', top: '50%', right: -12,
          transform: 'translateY(-50%)',
          width: 24, height: 24, borderRadius: '50%',
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-hover)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', color: 'var(--text-secondary)',
          transition: 'all 150ms ease-out', zIndex: 50,
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.color = 'var(--accent-gold)';
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent-gold)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
          (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-hover)';
        }}
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </aside>
  );
}

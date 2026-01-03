/**
 * Dashboard Layout Component
 *
 * Lab Workspace pattern layout for the YesBut application.
 * Header (48px) + Sidebar (240px) + Main Content + Panel (320px) + Footer (40px)
 *
 * @module app/dashboard/layout
 */

import type { ReactNode } from 'react';
import Link from 'next/link';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps): JSX.Element {
  return (
    <div className="flex flex-col min-h-screen bg-paper">
      {/* Header - 48px */}
      <header className="h-12 border-b border-ink-20 bg-white flex items-center px-4 shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="font-semibold text-ink-100">
            YesBut
          </Link>
        </div>
        <div className="flex-1" />
        <div className="flex items-center gap-2">
          <span className="text-sm text-ink-60">User</span>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - 240px */}
        <aside className="w-60 border-r border-ink-20 bg-white flex flex-col shrink-0">
          <nav className="flex-1 p-3">
            <div className="mb-4">
              <h3 className="text-xs font-medium text-ink-40 uppercase tracking-wider mb-2 px-2">
                Navigation
              </h3>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 px-2 py-1.5 text-sm text-ink-80 hover:bg-ink-05 rounded-md transition-colors duration-fast"
              >
                Dashboard
              </Link>
              <Link
                href="/dashboard/sessions"
                className="flex items-center gap-2 px-2 py-1.5 text-sm text-ink-80 hover:bg-ink-05 rounded-md transition-colors duration-fast"
              >
                Sessions
              </Link>
            </div>
            <div className="mb-4">
              <h3 className="text-xs font-medium text-ink-40 uppercase tracking-wider mb-2 px-2">
                Recent Sessions
              </h3>
              <p className="px-2 text-xs text-ink-40">No sessions yet</p>
            </div>
          </nav>
          <div className="p-3 border-t border-ink-10">
            <Link
              href="/dashboard/sessions/new"
              className="flex items-center justify-center gap-2 w-full px-3 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-hover transition-colors duration-fast"
            >
              New Session
            </Link>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto bg-ink-05">
          {children}
        </main>
      </div>
    </div>
  );
}

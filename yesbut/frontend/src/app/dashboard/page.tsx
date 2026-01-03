/**
 * Dashboard Overview Page Component
 *
 * The main dashboard page showing user's brainstorming sessions overview.
 * Follows Scientific Minimalism design with ink-* color palette.
 *
 * @module app/dashboard/page
 */

'use client';

import Link from 'next/link';
import { useTranslation } from '@/i18n';

export default function DashboardPage(): JSX.Element {
  const t = useTranslation();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink-100">{t.dashboard.title}</h1>
        <p className="text-sm text-ink-60 mt-1">{t.dashboard.subtitle}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card">
          <h3 className="text-xs font-medium text-ink-40 uppercase tracking-wider">{t.dashboard.totalSessions}</h3>
          <p className="text-2xl font-semibold text-ink-100 mt-1">0</p>
        </div>
        <div className="card">
          <h3 className="text-xs font-medium text-ink-40 uppercase tracking-wider">{t.dashboard.active}</h3>
          <p className="text-2xl font-semibold text-ink-100 mt-1">0</p>
        </div>
        <div className="card">
          <h3 className="text-xs font-medium text-ink-40 uppercase tracking-wider">{t.dashboard.completed}</h3>
          <p className="text-2xl font-semibold text-ink-100 mt-1">0</p>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-ink-100">{t.dashboard.recentSessions}</h2>
          <Link
            href="/dashboard/sessions"
            className="text-sm text-primary hover:underline"
          >
            {t.common.viewAll}
          </Link>
        </div>
        <div className="text-center py-8">
          <p className="text-sm text-ink-40 mb-4">{t.dashboard.noSessions}</p>
          <Link
            href="/dashboard/sessions/new"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-hover transition-colors duration-fast"
          >
            {t.dashboard.createFirst}
          </Link>
        </div>
      </div>

      {/* Quick Start Guide */}
      <div className="card mt-6">
        <h2 className="text-base font-semibold text-ink-100 mb-4">{t.dashboard.howItWorks}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-phase-diverge/10 flex items-center justify-center shrink-0">
              <span className="text-sm font-semibold text-phase-diverge">1</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-ink-100">{t.phases.diverge}</h3>
              <p className="text-xs text-ink-60 mt-0.5">{t.phases.divergeDesc}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-phase-filter/10 flex items-center justify-center shrink-0">
              <span className="text-sm font-semibold text-phase-filter">2</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-ink-100">{t.phases.filter}</h3>
              <p className="text-xs text-ink-60 mt-0.5">{t.phases.filterDesc}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-phase-converge/10 flex items-center justify-center shrink-0">
              <span className="text-sm font-semibold text-phase-converge">3</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-ink-100">{t.phases.converge}</h3>
              <p className="text-xs text-ink-60 mt-0.5">{t.phases.convergeDesc}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

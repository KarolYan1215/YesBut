'use client';

import Link from 'next/link';
import { Header } from '@/components/layout';
import { SessionCard } from '@/components/session';
import { useTranslation } from '@/i18n';

const sessions = [
  { id: '1', title: 'Product Strategy Q1', phase: 'filtering' as const, nodeCount: 24, updatedAt: '2 hours ago' },
  { id: '2', title: 'Marketing Campaign', phase: 'divergence' as const, nodeCount: 12, updatedAt: '1 day ago' },
  { id: '3', title: 'Tech Architecture Review', phase: 'completed' as const, nodeCount: 48, updatedAt: '3 days ago' },
  { id: '4', title: 'Q4 Planning', phase: 'convergence' as const, nodeCount: 36, updatedAt: '5 days ago' },
];

export default function SessionsListPage(): JSX.Element {
  const t = useTranslation();

  return (
    <div className="h-full">
      <Header
        title={t.sessions.title}
        actions={
          <Link href="/dashboard/sessions/new" className="btn-primary">
            {t.sessions.newSession}
          </Link>
        }
      />

      <div className="p-6">
        <div className="space-y-3">
          {sessions.map((session) => (
            <SessionCard
              key={session.id}
              id={session.id}
              title={session.title}
              phase={session.phase}
              nodeCount={session.nodeCount}
              updatedAt={session.updatedAt}
            />
          ))}
        </div>

        {sessions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted mb-4">{t.dashboard.noSessions}</p>
            <Link href="/dashboard/sessions/new" className="btn-primary">
              {t.dashboard.createFirst}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

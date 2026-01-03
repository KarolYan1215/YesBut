'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout';
import { Button } from '@/components/ui';
import { useTranslation } from '@/i18n';

export default function NewSessionPage(): JSX.Element {
  const router = useRouter();
  const t = useTranslation();
  const [title, setTitle] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: API call to create session
    router.push('/dashboard/sessions/1');
  };

  return (
    <div className="h-full">
      <Header
        title={t.sessions.newSession.replace('+ ', '')}
        showBack
        backHref="/dashboard/sessions"
      />

      <div className="p-6 max-w-lg">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              {t.sessions.sessionTitle}
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t.sessions.titlePlaceholder}
              className="input"
              required
              autoFocus
            />
            <p className="text-xs text-muted mt-2">
              {t.sessions.goalPlaceholder}
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
            >
              {t.common.cancel}
            </Button>
            <Button type="submit" disabled={!title.trim()}>
              {t.sessions.createSession}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

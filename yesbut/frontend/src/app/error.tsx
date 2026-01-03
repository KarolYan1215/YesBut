'use client';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps): JSX.Element {
  return (
    <div className="min-h-screen flex items-center justify-center bg-paper p-4">
      <div className="max-w-md w-full bg-white border border-ink-20 rounded-md p-6 text-center">
        <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-signal-critical/10 flex items-center justify-center">
          <svg className="w-6 h-6 text-signal-critical" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
        </div>
        <h1 className="text-lg font-semibold text-ink-100 mb-2">Something went wrong</h1>
        <p className="text-sm text-ink-60 mb-4">
          {process.env.NODE_ENV === 'development' ? error.message : 'An unexpected error occurred'}
        </p>
        {error.digest && (
          <p className="text-xs font-mono text-ink-40 mb-4">Error ID: {error.digest}</p>
        )}
        <div className="flex gap-2 justify-center">
          <button
            onClick={reset}
            className="px-4 py-2 text-sm font-medium bg-ink-100 text-white rounded hover:bg-ink-80 transition-colors"
          >
            Try again
          </button>
          <a
            href="/"
            className="px-4 py-2 text-sm font-medium border border-ink-20 text-ink-80 rounded hover:bg-ink-05 transition-colors"
          >
            Go home
          </a>
        </div>
      </div>
    </div>
  );
}

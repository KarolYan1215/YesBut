'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage(): JSX.Element {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, rememberMe }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Login failed');
      }

      const data = await res.json();
      localStorage.setItem('auth_token', data.token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper p-4">
      <div className="max-w-sm w-full">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-ink-100">Sign in to YesBut</h1>
          <p className="text-sm text-ink-60 mt-1">Multi-agent collaborative brainstorming</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white border border-ink-20 rounded-md p-6 space-y-4">
          {error && (
            <div className="p-3 bg-signal-critical/10 border border-signal-critical/20 rounded text-sm text-signal-critical">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-ink-60 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-ink-60 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-ink-60">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded border-ink-20"
              />
              Remember me
            </label>
            <Link href="/forgot-password" className="text-sm text-ink-60 hover:text-ink-100">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 bg-ink-100 text-white text-sm font-medium rounded hover:bg-ink-80 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-sm text-ink-60 mt-4">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-ink-100 hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}

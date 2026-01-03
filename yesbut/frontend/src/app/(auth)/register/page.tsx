'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage(): JSX.Element {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const getPasswordStrength = (pwd: string): { level: number; label: string } => {
    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
    if (/\d/.test(pwd)) score++;
    if (/[^a-zA-Z0-9]/.test(pwd)) score++;
    const labels = ['Weak', 'Fair', 'Good', 'Strong'];
    return { level: score, label: labels[Math.max(0, score - 1)] || 'Weak' };
  };

  const strength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (!acceptTerms) {
      setError('Please accept the terms of service');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Registration failed');
      }

      router.push('/login?registered=true');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper p-4">
      <div className="max-w-sm w-full">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-ink-100">Create account</h1>
          <p className="text-sm text-ink-60 mt-1">Start brainstorming with AI agents</p>
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
              minLength={8}
              className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
            />
            {password && (
              <div className="mt-2">
                <div className="flex gap-1">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded ${
                        i <= strength.level
                          ? strength.level <= 1 ? 'bg-signal-critical' : strength.level <= 2 ? 'bg-signal-warning' : 'bg-signal-success'
                          : 'bg-ink-10'
                      }`}
                    />
                  ))}
                </div>
                <p className="text-[10px] text-ink-40 mt-1">{strength.label}</p>
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-ink-60 mb-1">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
            />
          </div>

          <label className="flex items-start gap-2 text-sm text-ink-60">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              className="mt-0.5 rounded border-ink-20"
            />
            <span>
              I agree to the{' '}
              <Link href="/terms" className="text-ink-100 hover:underline">Terms of Service</Link>
            </span>
          </label>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 bg-ink-100 text-white text-sm font-medium rounded hover:bg-ink-80 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p className="text-center text-sm text-ink-60 mt-4">
          Already have an account?{' '}
          <Link href="/login" className="text-ink-100 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center min-h-[70vh] px-8">
        <h1 className="text-5xl font-bold text-foreground mb-4 tracking-tight">
          YesBut
        </h1>
        <p className="text-xl text-muted mb-8 text-center max-w-md">
          Multi-Agent Collaborative Brainstorming System
        </p>

        <Link
          href="/dashboard"
          className="btn-primary px-8 py-3 text-base rounded-lg"
        >
          Get Started
        </Link>

        {/* Phase Indicator */}
        <div className="flex items-center gap-4 mt-16">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-phase-diverge" />
            <span className="text-sm text-muted">Diverge</span>
          </div>
          <div className="w-8 h-px bg-border" />
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-phase-filter" />
            <span className="text-sm text-muted">Filter</span>
          </div>
          <div className="w-8 h-px bg-border" />
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-phase-converge" />
            <span className="text-sm text-muted">Converge</span>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-4xl mx-auto px-8 pb-20">
        <div className="grid grid-cols-3 gap-6">
          <div className="card text-center">
            <div className="w-10 h-10 rounded-full bg-phase-diverge/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-5 h-5 text-phase-diverge" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-foreground mb-2">Divergence</h3>
            <p className="text-sm text-muted">
              Generate diverse solutions using Quality-Diversity algorithms
            </p>
          </div>

          <div className="card text-center">
            <div className="w-10 h-10 rounded-full bg-phase-filter/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-5 h-5 text-phase-filter" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </div>
            <h3 className="font-semibold text-foreground mb-2">Filtering</h3>
            <p className="text-sm text-muted">
              Multi-objective Pareto optimization for candidate selection
            </p>
          </div>

          <div className="card text-center">
            <div className="w-10 h-10 rounded-full bg-phase-converge/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-5 h-5 text-phase-converge" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="font-semibold text-foreground mb-2">Convergence</h3>
            <p className="text-sm text-muted">
              N-player game theory for multi-agent consensus
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

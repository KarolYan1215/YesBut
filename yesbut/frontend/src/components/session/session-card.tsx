import Link from 'next/link';
import { Badge } from '@/components/ui';
import { PhaseIndicator } from './phase-indicator';

type Phase = 'divergence' | 'filtering' | 'convergence' | 'completed';

interface SessionCardProps {
  id: string;
  title: string;
  phase: Phase;
  nodeCount: number;
  updatedAt: string;
}

export function SessionCard({ id, title, phase, nodeCount, updatedAt }: SessionCardProps) {
  return (
    <Link href={`/dashboard/sessions/${id}`}>
      <div className="card hover:shadow-md hover:border-primary/20 transition-all cursor-pointer">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-medium text-foreground mb-1">{title}</h3>
            <div className="flex items-center gap-4 text-sm text-muted">
              <span>{nodeCount} nodes</span>
              <span>{updatedAt}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <PhaseIndicator currentPhase={phase} />
            {phase === 'completed' && (
              <Badge variant="success">Completed</Badge>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

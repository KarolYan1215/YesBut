'use client';

import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';

export interface Constraint {
  id: string;
  type: 'hard' | 'soft';
  content: string;
}

interface ConstraintEditorProps {
  constraints: Constraint[];
  onChange: (constraints: Constraint[]) => void;
  maxConstraints?: number;
}

export function ConstraintEditor({
  constraints,
  onChange,
  maxConstraints = 10,
}: ConstraintEditorProps) {
  const [newConstraint, setNewConstraint] = useState('');
  const [constraintType, setConstraintType] = useState<'hard' | 'soft'>('hard');

  const addConstraint = () => {
    if (!newConstraint.trim() || constraints.length >= maxConstraints) return;

    const constraint: Constraint = {
      id: `constraint-${Date.now()}`,
      type: constraintType,
      content: newConstraint.trim(),
    };

    onChange([...constraints, constraint]);
    setNewConstraint('');
  };

  const removeConstraint = (id: string) => {
    onChange(constraints.filter((c) => c.id !== id));
  };

  const toggleType = (id: string) => {
    onChange(
      constraints.map((c) =>
        c.id === id ? { ...c, type: c.type === 'hard' ? 'soft' : 'hard' } : c
      )
    );
  };

  return (
    <div className="space-y-4">
      {/* Constraint list */}
      {constraints.length > 0 && (
        <div className="space-y-2">
          {constraints.map((constraint) => (
            <div
              key={constraint.id}
              className={`flex items-center gap-3 p-3 rounded-lg border ${
                constraint.type === 'hard'
                  ? 'border-red-200 bg-red-50'
                  : 'border-orange-200 bg-orange-50'
              }`}
            >
              <button
                onClick={() => toggleType(constraint.id)}
                className="shrink-0"
              >
                <Badge variant={constraint.type === 'hard' ? 'error' : 'warning'}>
                  {constraint.type === 'hard' ? 'Hard' : 'Soft'}
                </Badge>
              </button>
              <span className="flex-1 text-sm">{constraint.content}</span>
              <button
                onClick={() => removeConstraint(constraint.id)}
                className="p-1 hover:bg-white/50 rounded transition-colors"
              >
                <svg className="w-4 h-4 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new constraint */}
      {constraints.length < maxConstraints && (
        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              value={newConstraint}
              onChange={(e) => setNewConstraint(e.target.value)}
              placeholder="Add a constraint..."
              onKeyDown={(e) => e.key === 'Enter' && addConstraint()}
            />
          </div>
          <select
            value={constraintType}
            onChange={(e) => setConstraintType(e.target.value as 'hard' | 'soft')}
            className="px-3 py-2 border border-border rounded-lg bg-surface text-sm"
          >
            <option value="hard">Hard</option>
            <option value="soft">Soft</option>
          </select>
          <Button onClick={addConstraint} disabled={!newConstraint.trim()}>
            Add
          </Button>
        </div>
      )}

      {/* Help text */}
      <div className="text-xs text-muted">
        <p><strong>Hard constraints:</strong> Must be satisfied (e.g., budget limits)</p>
        <p><strong>Soft constraints:</strong> Preferences that can be relaxed</p>
      </div>
    </div>
  );
}

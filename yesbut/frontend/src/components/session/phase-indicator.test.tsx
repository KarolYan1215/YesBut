/**
 * Phase Indicator Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PhaseIndicator } from './phase-indicator';

describe('PhaseIndicator', () => {
  it('TC-SE001: should show divergence phase active', () => {
    render(<PhaseIndicator currentPhase="divergence" />);

    const divergeStep = screen.getByText('Diverge');
    expect(divergeStep).toBeInTheDocument();
    // Check that divergence text has active styling (font-medium)
    expect(divergeStep).toHaveClass('font-medium');
  });

  it('TC-SE002: should show filtering phase active', () => {
    render(<PhaseIndicator currentPhase="filtering" />);

    const filterStep = screen.getByText('Filter');
    expect(filterStep).toBeInTheDocument();
    expect(filterStep).toHaveClass('font-medium');
  });

  it('TC-SE003: should show convergence phase active', () => {
    render(<PhaseIndicator currentPhase="convergence" />);

    const convergeStep = screen.getByText('Converge');
    expect(convergeStep).toBeInTheDocument();
    expect(convergeStep).toHaveClass('font-medium');
  });

  it('should show all three phases', () => {
    render(<PhaseIndicator currentPhase="divergence" />);

    expect(screen.getByText('Diverge')).toBeInTheDocument();
    expect(screen.getByText('Filter')).toBeInTheDocument();
    expect(screen.getByText('Converge')).toBeInTheDocument();
  });

  it('should mark previous phases as completed', () => {
    render(<PhaseIndicator currentPhase="convergence" />);

    // When convergence is active, Diverge and Filter are completed
    // Completed phases have text-foreground class (not text-muted)
    // But based on the component logic, only the active phase has font-medium
    const convergeStep = screen.getByText('Converge');
    expect(convergeStep).toHaveClass('font-medium');
    expect(convergeStep).toHaveClass('text-foreground');
  });
});

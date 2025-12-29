/**
 * Graph Heatmap Overlay Component
 *
 * Renders a semi-transparent heatmap overlay on the graph canvas
 * to visualize conflict intensity, confidence distribution, or sensitivity.
 *
 * @module components/graph/graph-heatmap
 */

/**
 * Heatmap visualization mode
 */
type HeatmapMode = 'conflict' | 'confidence' | 'sensitivity';

/**
 * Props interface for GraphHeatmap component
 */
interface GraphHeatmapProps {
  /**
   * The current heatmap visualization mode
   * - 'conflict': Shows edge attack intensity
   * - 'confidence': Shows node confidence distribution
   * - 'sensitivity': Shows node criticality for stability analysis
   */
  mode: HeatmapMode;

  /**
   * Whether the heatmap overlay is visible
   */
  visible: boolean;

  /**
   * Callback to change the heatmap mode
   */
  onModeChange: (mode: HeatmapMode) => void;

  /**
   * Callback to toggle heatmap visibility
   */
  onToggleVisibility: () => void;
}

/**
 * Graph heatmap overlay component
 *
 * Renders a color-coded overlay on the graph to visualize:
 * - Conflict mode: Red intensity based on attack edge weights
 * - Confidence mode: Green-yellow-red gradient based on node confidence
 * - Sensitivity mode: Blue-purple gradient based on criticality scores
 *
 * The heatmap is computed using utilities from heatmap-utils.ts
 *
 * @param props - Component props
 * @returns The graph heatmap JSX element
 */
export function GraphHeatmap(props: GraphHeatmapProps): JSX.Element {
  // TODO: Implement heatmap overlay with mode switching
  // TODO: Compute heatmap data based on mode
  throw new Error('Not implemented');
}

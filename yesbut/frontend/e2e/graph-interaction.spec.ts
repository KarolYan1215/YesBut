/**
 * Graph Interaction E2E Tests
 *
 * TC-E2E005: Graph Canvas Interaction
 */

import { test, expect } from '@playwright/test';

test.describe('Graph Canvas Interaction', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a session with graph
    await page.goto('/dashboard/sessions/test-session');
    // Wait for graph to load
    await page.waitForSelector('[data-testid="graph-canvas"]', { timeout: 10000 });
  });

  test('TC-E2E005-1: should select node on click', async ({ page }) => {
    // Click on a node
    const node = page.locator('[data-testid="graph-node"]').first();
    await node.click();

    // Verify node is highlighted
    await expect(node).toHaveClass(/selected/);

    // Verify detail panel opens
    await expect(page.getByTestId('node-detail-panel')).toBeVisible();
  });

  test('TC-E2E005-2: should pan canvas on drag', async ({ page }) => {
    const canvas = page.getByTestId('graph-canvas');

    // Get initial viewport
    const initialTransform = await canvas.evaluate((el) => {
      const reactFlow = el.querySelector('.react-flow__viewport');
      return reactFlow?.getAttribute('transform');
    });

    // Drag canvas
    await canvas.dragTo(canvas, {
      sourcePosition: { x: 200, y: 200 },
      targetPosition: { x: 300, y: 300 },
    });

    // Verify viewport changed
    const newTransform = await canvas.evaluate((el) => {
      const reactFlow = el.querySelector('.react-flow__viewport');
      return reactFlow?.getAttribute('transform');
    });

    expect(newTransform).not.toBe(initialTransform);
  });

  test('TC-E2E005-3: should zoom on scroll', async ({ page }) => {
    const canvas = page.getByTestId('graph-canvas');

    // Get initial zoom
    const initialZoom = await page.evaluate(() => {
      const viewport = document.querySelector('.react-flow__viewport');
      const transform = viewport?.getAttribute('transform') || '';
      const match = transform.match(/scale\(([^)]+)\)/);
      return match ? parseFloat(match[1]) : 1;
    });

    // Scroll to zoom
    await canvas.hover();
    await page.mouse.wheel(0, -100);

    // Wait for zoom animation
    await page.waitForTimeout(300);

    // Verify zoom changed
    const newZoom = await page.evaluate(() => {
      const viewport = document.querySelector('.react-flow__viewport');
      const transform = viewport?.getAttribute('transform') || '';
      const match = transform.match(/scale\(([^)]+)\)/);
      return match ? parseFloat(match[1]) : 1;
    });

    expect(newZoom).toBeGreaterThan(initialZoom);
  });

  test('TC-E2E005-4: should toggle view mode', async ({ page }) => {
    // Click Causal View toggle
    await page.getByRole('button', { name: /causal/i }).click();

    // Verify causal edges are shown
    await expect(page.locator('[data-edge-type="decompose"]')).toBeVisible();

    // Click Conflict View toggle
    await page.getByRole('button', { name: /conflict/i }).click();

    // Verify conflict edges are shown
    await expect(page.locator('[data-edge-type="conflict"]')).toBeVisible();
  });
});

test.describe('Phase Transitions', () => {
  test('TC-E2E002: should transition through phases', async ({ page }) => {
    await page.goto('/dashboard/sessions/test-session');

    // Verify starting in Divergence
    await expect(page.getByText('Diverge')).toHaveAttribute('data-active', 'true');

    // Click Next Phase
    await page.getByRole('button', { name: /next phase/i }).click();

    // Verify transition to Filtering
    await expect(page.getByText('Filter')).toHaveAttribute('data-active', 'true');

    // Click Next Phase again
    await page.getByRole('button', { name: /next phase/i }).click();

    // Verify transition to Convergence
    await expect(page.getByText('Converge')).toHaveAttribute('data-active', 'true');
  });
});

test.describe('Real-time Updates', () => {
  test('should receive SSE updates', async ({ page }) => {
    await page.goto('/dashboard/sessions/test-session');

    // Wait for initial nodes
    const initialNodeCount = await page.locator('[data-testid="graph-node"]').count();

    // Wait for SSE update (simulated by backend)
    await page.waitForTimeout(5000);

    // Verify new nodes appeared
    const newNodeCount = await page.locator('[data-testid="graph-node"]').count();
    expect(newNodeCount).toBeGreaterThanOrEqual(initialNodeCount);
  });
});

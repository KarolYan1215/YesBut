/**
 * Session Creation E2E Tests
 *
 * TC-E2E001: Complete Session Creation Flow
 */

import { test, expect } from '@playwright/test';

test.describe('Session Creation Flow', () => {
  test('TC-E2E001: should complete full session creation flow', async ({ page }) => {
    // Step 1: Navigate to Landing Page
    await page.goto('/');
    await expect(page).toHaveTitle(/YesBut/);

    // Click Get Started button
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    if (await getStartedButton.isVisible()) {
      await getStartedButton.click();
    } else {
      // Direct navigation if no button
      await page.goto('/dashboard');
    }

    // Step 2: Navigate to Dashboard
    await expect(page).toHaveURL(/dashboard/);

    // Click New Session button
    await page.getByRole('link', { name: /new session/i }).click();

    // Step 3: Fill Session Form
    await expect(page).toHaveURL(/sessions\/new/);

    // Enter title
    await page.getByLabel(/session title/i).fill('Product Strategy Q1 2025');

    // Enter goal
    await page.getByLabel(/goal|requirement/i).fill(
      'Develop a comprehensive product roadmap for Q1'
    );

    // Select mode (Async)
    await page.getByText('Async').click();

    // Submit form
    await page.getByRole('button', { name: /create session/i }).click();

    // Step 4: Verify Session Created
    await expect(page).toHaveURL(/sessions\/\w+/);

    // Verify session title displayed
    await expect(page.getByText('Product Strategy Q1 2025')).toBeVisible();

    // Verify phase indicator shows Divergence
    await expect(page.getByText('Diverge')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/dashboard/sessions/new');

    // Try to submit without filling required fields
    await page.getByRole('button', { name: /create session/i }).click();

    // Should show validation errors or stay on page
    await expect(page).toHaveURL(/sessions\/new/);
  });

  test('should allow mode selection', async ({ page }) => {
    await page.goto('/dashboard/sessions/new');

    // Select Sync mode
    await page.getByText('Sync').click();

    // Verify Sync is selected
    const syncCard = page.getByText('Sync').locator('..');
    await expect(syncCard).toHaveClass(/border-primary/);
  });
});

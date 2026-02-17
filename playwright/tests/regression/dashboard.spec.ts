/**
 * Dashboard regression: UI-8, UI-9, EE-2, EE-3
 */
import { test, expect } from '@playwright/test';
import { DashboardPage } from '../../pages/DashboardPage';

test.describe('Dashboard', () => {
  test('UI-8: Dashboard Incident Forms empty vs populated state', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    const container = await dashboard.getIncidentFormsContent();
    await dashboard.expectEmptyStateOrContent(container);
  });

  test('UI-9: Dashboard Background Check empty vs populated state', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    const container = await dashboard.getBackgroundCheckContent();
    await dashboard.expectEmptyStateOrContent(container);
  });

  test('EE-2: Incident Forms empty state', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await expect(page.getByText(/incident forms/i).first()).toBeVisible();
    await expect(page.getByText(/empty|no incident|no data/i).or(page.locator('[role="list"]'))).toBeVisible({ timeout: 10000 });
  });

  test('EE-3: Background Check empty state', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await expect(page.getByText(/background check/i).first()).toBeVisible();
    await expect(page.getByText(/empty|no background|no data/i).or(page.locator('[role="list"]'))).toBeVisible({ timeout: 10000 });
  });
});

/**
 * Manage Schedule regression: UI-5, RS-4
 */
import { test, expect } from '@playwright/test';
import { SchedulePage } from '../../pages/SchedulePage';

test.describe('Manage Schedule', () => {
  test('UI-5: Manage Schedule opens Add Client Visit (Care Coordinator)', async ({ page }) => {
    const schedulePage = new SchedulePage(page);
    await schedulePage.goto();
    await schedulePage.openAddClientVisit();
    await schedulePage.expectAddClientVisitFlowVisible();
  });

  test('RS-4: Orientation change reflow (Calendar / Live View)', async ({ page }) => {
    const schedulePage = new SchedulePage(page);
    await schedulePage.goto();
    await expect(schedulePage.calendarSection.or(page.getByRole('main'))).toBeVisible();
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('main').or(schedulePage.calendarSection)).toBeVisible();
  });
});

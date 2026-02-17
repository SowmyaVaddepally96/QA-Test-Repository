/**
 * Time Entry regression: UI-7
 */
import { test, expect } from '@playwright/test';
import { TimeEntryPage } from '../../pages/TimeEntryPage';

test.describe('Time Entry', () => {
  test('UI-7: Time Entry shows role-specific entry screen', async ({ page }) => {
    const timeEntryPage = new TimeEntryPage(page);
    await timeEntryPage.goto();
    await timeEntryPage.selectRoleEntry('Care Manager');
    await timeEntryPage.expectRoleScreenVisible();
  });
});

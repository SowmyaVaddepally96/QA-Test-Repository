/**
 * Manage Clients regression: UI-6
 */
import { test, expect } from '@playwright/test';
import { ClientListPage } from '../../pages/ClientListPage';

test.describe('Manage Clients', () => {
  test('UI-6: Manage Clients opens Add Client flow', async ({ page }) => {
    const listPage = new ClientListPage(page);
    await listPage.goto();
    await listPage.openAddClient();
    await listPage.expectAddClientFlowVisible();
  });
});

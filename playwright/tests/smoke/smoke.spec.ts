/**
 * Smoke suite: UI-1, UI-2, EE-1 (critical path)
 * Run first to validate app is up and auth works.
 */
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPage';
import { DashboardPage } from '../../pages/DashboardPage';
import { testUser } from '../../utils/env';

test.describe('Smoke', () => {
  test('Login with valid credentials reaches main app', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    await loginPage.goto();
    await loginPage.login(testUser.valid.email, testUser.valid.password);
    await expect(page).toHaveURL(/\/(dashboard|plan-of-care)/);
    await dashboardPage.expectMainAppVisible();
  });

  test('Restricted user sees no permission message', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(testUser.restricted.email, testUser.restricted.password);
    await expect(page.getByText(/no permission|access denied|restricted/i)).toBeVisible();
  });
});

/**
 * Auth tests from normalized cases: UI-1, UI-2, EE-1
 * Tags: smoke, happy-path, negative, auth
 */
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPage';
import { DashboardPage } from '../../pages/DashboardPage';
import { testUser } from '../../utils/env';

test.describe('Authentication', () => {
  test('UI-1: Login with valid credentials redirects to main app @smoke @happy-path @auth', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await loginPage.goto();
    await loginPage.login(testUser.valid.email, testUser.valid.password);

    await expect(page).toHaveURL(/\/(dashboard|plan-of-care)/);
    await dashboardPage.expectMainAppVisible();
  });

  test('UI-2: Login with restricted role shows no permission message @smoke @negative @auth', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login(testUser.restricted.email, testUser.restricted.password);

    await loginPage.expectNoPermissionMessage();
    await loginPage.expectStillOnLogin();
  });

  test('EE-1: No permission message on restricted access @smoke @negative @auth', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login(testUser.restricted.email, testUser.restricted.password);

    await expect(page.getByText(/no permission|access denied|restricted/i)).toBeVisible();
  });
});

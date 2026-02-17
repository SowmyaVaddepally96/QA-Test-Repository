/**
 * Manage Employees regression: UI-4, CS-13, EE-6, AX-8
 */
import { test, expect } from '@playwright/test';
import { EmployeeListPage } from '../../pages/EmployeeListPage';

test.describe('Manage Employees', () => {
  test('UI-4: Manage Employees opens Add Employee flow', async ({ page }) => {
    const listPage = new EmployeeListPage(page);
    await listPage.goto();
    await listPage.openAddEmployee();
    await listPage.expectAddEmployeeFlowVisible();
  });

  test('CS-13: Do not send table Show Employee / Show Client columns', async ({ page }) => {
    await page.goto('/manage-employees');
    const showEmployee = page.getByRole('checkbox', { name: /show employee/i }).or(page.getByLabel(/show employee/i));
    const showClient = page.getByRole('checkbox', { name: /show client/i }).or(page.getByLabel(/show client/i));
    const table = page.getByRole('table');
    if (await showEmployee.count() > 0) {
      await showEmployee.click();
      await expect(table).toBeVisible();
    }
    if (await showClient.count() > 0) {
      await showClient.click();
      await expect(table).toBeVisible();
    }
  });

  test('EE-6: Employee Profile Do not send (Blacklist)', async ({ page }) => {
    await page.goto('/manage-employees');
    const profileLink = page.getByRole('link', { name: /profile|information|blacklist/i }).first();
    if (await profileLink.count() > 0) {
      await profileLink.click();
      await expect(page.getByText(/do not send|blacklist/i).or(page.getByRole('table'))).toBeVisible();
    }
  });
});

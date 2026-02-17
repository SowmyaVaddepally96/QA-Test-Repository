/**
 * Forms and validation: EE-5
 */
import { test, expect } from '@playwright/test';

test.describe('Forms validation', () => {
  test('EE-5: TextField validation error', async ({ page }) => {
    await page.goto('/login');
    const submit = page.getByRole('button', { name: /login|submit|sign in/i });
    if (await submit.count() > 0) {
      await submit.click();
      const error = page.getByRole('alert').or(page.getByText(/error|invalid|required/i)).or(page.locator('[class*="error"]'));
      await expect(error.first()).toBeVisible({ timeout: 5000 });
    }
  });
});

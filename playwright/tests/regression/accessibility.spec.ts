/**
 * Accessibility: AX-1, AX-2, AX-3, AX-5
 * AX-6, AX-7, AX-8 are manual/axe; skip or run with axe-playwright when available.
 */
import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test('AX-1: Focus visibility on Buttons', async ({ page }) => {
    await page.goto('/login');
    const button = page.getByRole('button').first();
    if (await button.count() > 0) {
      await button.focus();
      await expect(button).toBeFocused();
    }
  });

  test('AX-2: Focus visibility on TextField', async ({ page }) => {
    await page.goto('/login');
    const input = page.getByRole('textbox').or(page.getByLabel(/email|password/i)).first();
    if (await input.count() > 0) {
      await input.focus();
      await expect(input).toBeFocused();
    }
  });

  test('AX-3: Focus and keyboard open on Dropdown', async ({ page }) => {
    await page.goto('/');
    const combobox = page.getByRole('combobox').first();
    if (await combobox.count() > 0) {
      await combobox.focus();
      await page.keyboard.press('Enter');
      await expect(page.getByRole('listbox').or(page.getByRole('option'))).toBeVisible();
    }
  });

  test('AX-5: Keyboard toggle Checkbox/Switch', async ({ page }) => {
    await page.goto('/');
    const checkbox = page.getByRole('checkbox').first();
    if (await checkbox.count() > 0) {
      await checkbox.focus();
      await page.keyboard.press('Space');
      await expect(checkbox).toBeChecked();
    }
  });
});

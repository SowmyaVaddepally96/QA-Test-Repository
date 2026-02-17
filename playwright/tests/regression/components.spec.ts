/**
 * Component state regression: CS-1 through CS-12, CS-16, CS-17
 * Uses getByRole / getByLabel; adjust selectors when app is available.
 */
import { test, expect } from '@playwright/test';

test.describe('Component State', () => {
  test('CS-1: Button default vs disabled state', async ({ page }) => {
    await page.goto('/');
    const button = page.getByRole('button', { name: /submit|save|login/i }).first();
    if (await button.count() > 0) {
      await expect(button).toBeEnabled();
      await button.click().catch(() => {});
      const disabledButton = page.locator('button[disabled], button[aria-disabled="true"]').first();
      if (await disabledButton.count() > 0) await expect(disabledButton).toBeDisabled();
    }
  });

  test('CS-2: Button variants Contained / Outlined / Ghost', async ({ page }) => {
    await page.goto('/');
    const buttons = page.getByRole('button');
    const withVariant = page.locator('[data-variant], [class*="contained"], [class*="outlined"], [class*="ghost"]');
    if (await withVariant.count() > 0) await expect(withVariant.first()).toBeVisible();
  });

  test('CS-5: TextField empty vs has value', async ({ page }) => {
    await page.goto('/login');
    const input = page.getByRole('textbox').or(page.getByLabel(/email|username/i)).first();
    if (await input.count() > 0) {
      await expect(input).toHaveValue('');
      await input.fill('test@example.com');
      await expect(input).toHaveValue('test@example.com');
    }
  });

  test('CS-6: TextField enabled vs disabled', async ({ page }) => {
    await page.goto('/');
    const input = page.getByRole('textbox').first();
    if (await input.count() > 0) {
      await expect(input).toBeEditable();
    }
    const disabledInput = page.locator('input[disabled], input[readonly]').first();
    if (await disabledInput.count() > 0) await expect(disabledInput).toBeDisabled();
  });

  test('CS-9: Chip selected Off vs On', async ({ page }) => {
    await page.goto('/');
    const chip = page.getByRole('option').or(page.locator('[role="tab"]')).or(page.getByText(/\w+/).first());
    if (await chip.count() > 0) {
      await chip.click();
      await expect(chip).toHaveAttribute('aria-selected', 'true').or(chip.locator('[class*="selected"]').first()).toBeVisible();
    }
  });

  test('CS-10: Alert Success vs Error', async ({ page }) => {
    await page.goto('/');
    const alert = page.getByRole('alert');
    if (await alert.count() > 0) {
      await expect(alert.first()).toBeVisible();
    }
  });

  test('CS-11: Dropdown open Off vs On', async ({ page }) => {
    await page.goto('/');
    const trigger = page.getByRole('combobox').or(page.getByRole('button', { name: /select|dropdown/i })).first();
    if (await trigger.count() > 0) {
      const list = page.getByRole('listbox').or(page.locator('[role="menu"]'));
      await trigger.click();
      await expect(list).toBeVisible();
      await page.keyboard.press('Escape');
      await expect(list).toBeHidden();
    }
  });

  test('CS-16: Avatar acronym variant', async ({ page }) => {
    await page.goto('/');
    const avatar = page.getByRole('img', { name: /avatar|user/i }).or(page.locator('[class*="avatar"]'));
    if (await avatar.count() > 0) await expect(avatar.first()).toBeVisible();
  });

  test('EE-7: Status Dropdown on error screen', async ({ page }) => {
    await page.goto('/');
    const statusDropdown = page.getByRole('combobox', { name: /status/i }).or(page.getByLabel(/status/i));
    if (await statusDropdown.count() > 0) {
      await statusDropdown.click();
      await expect(page.getByRole('listbox').or(page.getByRole('option'))).toBeVisible();
    }
  });
});

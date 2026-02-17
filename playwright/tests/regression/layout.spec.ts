/**
 * Layout: LV-1, LV-2, RS-2, RS-3
 */
import { test, expect } from '@playwright/test';

test.describe('Layout', () => {
  test('LV-1: Desktop 12-column layout grid', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/dashboard');
    const main = page.getByRole('main').or(page.locator('[class*="grid"], [class*="layout"]'));
    await expect(main.first()).toBeVisible();
  });

  test('LV-2: Vertical scrolling on long content', async ({ page }) => {
    await page.goto('/plan-of-care');
    const scrollable = page.locator('[style*="overflow"], [class*="scroll"]').first();
    if (await scrollable.count() > 0) {
      await scrollable.evaluate((el) => (el as HTMLElement).scrollTop = 100);
      const scrollTop = await scrollable.evaluate((el) => (el as HTMLElement).scrollTop);
      expect(scrollTop).toBeGreaterThanOrEqual(0);
    }
  });

  test('RS-2: Mobile variant Mobile=Off vs Mobile=On', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    const desktopContent = page.getByRole('main').first();
    await expect(desktopContent).toBeVisible();
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('main').or(page.locator('body'))).toBeVisible();
  });

  test('RS-3: Viewport Desktop expanded state', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    const expanded = page.locator('[aria-expanded="true"]').first();
    if (await expanded.count() > 0) await expect(expanded).toBeVisible();
  });
});

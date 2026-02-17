/**
 * Plan of Care regression: UI-3, CS-8, CS-14, CS-15, EE-4, AX-4
 */
import { test, expect } from '@playwright/test';
import { PlanOfCarePage } from '../../pages/PlanOfCarePage';
test.describe('Plan of Care', () => {
  test('UI-3: Plan of Care opens Client Overview', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    await pocPage.openClientOverview();
    await pocPage.expectClientOverviewVisible();
  });

  test('CS-8: PoC Tabs default vs active', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    const tabs = pocPage.pocTabs;
    await expect(tabs.first()).toBeVisible();
    await pocPage.selectTab(0);
    await expect(tabs.first()).toHaveAttribute('aria-selected', 'true');
  });

  test('CS-14: Plan of Care domain variants displayed', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    const domains = page.getByText(/medical|client overview|care coordination|functional|cognitive|social|environmental|financial|legal/i);
    await expect(domains.first()).toBeVisible();
  });

  test('CS-15: Expandable section Expanded and Draft states', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    const expandable = pocPage.expandableSections.first();
    if (await expandable.count() > 0) {
      await expandable.click();
      await expect(expandable).toHaveAttribute('aria-expanded', 'true');
    }
  });

  test('EE-4: Plan of Care Medical Domain empty', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    const emptyMessage = pocPage.medicalDomainEmpty;
    await expect(emptyMessage.or(page.getByText(/no medical|empty/i))).toBeVisible({ timeout: 10000 });
  });

  test('AX-4: Keyboard navigation for PoC Tabs', async ({ page }) => {
    const pocPage = new PlanOfCarePage(page);
    await pocPage.goto();
    await pocPage.pocTabs.first().focus();
    await page.keyboard.press('ArrowRight');
    const selected = page.locator('[role="tab"][aria-selected="true"]');
    await expect(selected).toBeVisible();
  });
});

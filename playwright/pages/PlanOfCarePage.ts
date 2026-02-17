import { type Page, type Locator } from '@playwright/test';

export class PlanOfCarePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/plan-of-care');
  }

  get clientOverviewLink(): Locator {
    return this.page.getByRole('link', { name: /client overview/i }).or(this.page.getByText(/client overview/i));
  }

  get clientOverviewSection(): Locator {
    return this.page.getByTestId('client-overview').or(this.page.getByRole('region', { name: /client overview/i }));
  }

  get pocTabs(): Locator {
    return this.page.getByRole('tablist').locator('[role="tab"]');
  }

  async openClientOverview() {
    await this.clientOverviewLink.click();
  }

  async expectClientOverviewVisible() {
    await this.clientOverviewSection.waitFor({ state: 'visible' });
  }

  async selectTab(name: string | number) {
    const tab = typeof name === 'number' ? this.pocTabs.nth(name) : this.page.getByRole('tab', { name });
    await tab.click();
  }

  get expandableSections(): Locator {
    return this.page.getByRole('button', { name: /expand|collapse/i }).or(this.page.locator('[aria-expanded]'));
  }

  get medicalDomainEmpty(): Locator {
    return this.page.getByText(/medical domain empty|no medical/i).first();
  }
}

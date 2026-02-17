import { type Page, type Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async expectMainAppVisible() {
    await this.page.waitForURL(/\/(dashboard|plan-of-care)/);
    const navOrContent = this.page.getByRole('navigation').or(this.page.getByTestId('dashboard')).or(this.page.getByRole('main'));
    await navOrContent.first().waitFor({ state: 'visible' });
  }

  get incidentFormsSection(): Locator {
    return this.page.getByText(/incident forms/i).first();
  }

  get backgroundCheckSection(): Locator {
    return this.page.getByText(/background check/i).first();
  }

  async getIncidentFormsContent() {
    const section = this.incidentFormsSection;
    await section.waitFor({ state: 'visible' });
    return section.locator('..');
  }

  async getBackgroundCheckContent() {
    const section = this.backgroundCheckSection;
    await section.waitFor({ state: 'visible' });
    return section.locator('..');
  }

  async expectEmptyStateOrContent(container: Locator) {
    await expect(container.getByText(/empty|no (data|results)|no incident|no background/i).or(container.locator('table, [role="list"]'))).toBeVisible();
  }
}

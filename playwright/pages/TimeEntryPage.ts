import { type Page, type Locator } from '@playwright/test';

export class TimeEntryPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/time-entry');
  }

  get roleSelector(): Locator {
    return this.page.getByRole('tab', { name: /care manager|admin|care partner/i }).or(this.page.getByRole('button', { name: /care manager|admin|care partner/i }));
  }

  async selectRoleEntry(roleName: string) {
    await this.page.getByRole('tab', { name: new RegExp(roleName, 'i') }).or(this.page.getByRole('button', { name: new RegExp(roleName, 'i') })).click();
  }

  async expectRoleScreenVisible() {
    await this.page.getByRole('heading').or(this.page.getByRole('form')).first().waitFor({ state: 'visible' });
  }
}

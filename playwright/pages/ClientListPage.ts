import { type Page, type Locator } from '@playwright/test';

export class ClientListPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/manage-clients');
  }

  get addClientButton(): Locator {
    return this.page.getByRole('button', { name: /add client/i }).or(this.page.getByRole('link', { name: /add client/i }));
  }

  async openAddClient() {
    await this.addClientButton.click();
  }

  async expectAddClientFlowVisible() {
    await this.page.getByRole('form').or(this.page.getByText(/add client/i)).first().waitFor({ state: 'visible' });
  }
}

import { type Page, type Locator } from '@playwright/test';

export class SchedulePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/manage-schedule');
  }

  get addClientVisitButton(): Locator {
    return this.page.getByRole('button', { name: /add client visit|care coordinator/i }).or(this.page.getByText(/add client visit/i)).first();
  }

  get calendarSection(): Locator {
    return this.page.getByRole('application', { name: /calendar/i }).or(this.page.getByTestId('calendar')).or(this.page.getByText(/calendar/i).first());
  }

  async openAddClientVisit() {
    await this.addClientVisitButton.click();
  }

  async expectAddClientVisitFlowVisible() {
    await this.page.getByRole('dialog').or(this.page.getByText(/add client visit/i)).first().waitFor({ state: 'visible' });
  }
}

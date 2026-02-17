import { type Page, type Locator } from '@playwright/test';

export class EmployeeListPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/manage-employees');
  }

  get addEmployeeButton(): Locator {
    return this.page.getByRole('button', { name: /add (employee|entries)|add\/edit employee/i }).or(this.page.getByRole('link', { name: /add employee/i }));
  }

  get employeeList(): Locator {
    return this.page.getByRole('table').or(this.page.getByTestId('employee-list'));
  }

  async openAddEmployee() {
    await this.addEmployeeButton.click();
  }

  async expectAddEmployeeFlowVisible() {
    await this.page.getByRole('form').or(this.page.getByText(/add employee|edit employee/i)).first().waitFor({ state: 'visible' });
  }
}

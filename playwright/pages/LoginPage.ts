import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByRole('textbox', { name: /email|username|login/i }).or(page.getByLabel(/email|username|login/i));
    this.passwordInput = page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i));
    this.submitButton = page.getByRole('button', { name: /login|sign in|submit/i });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectNoPermissionMessage() {
    await this.page.getByText(/no permission|access denied|restricted/i).waitFor({ state: 'visible' });
  }

  async expectStillOnLogin() {
    await this.page.waitForURL(/\/login/);
  }
}

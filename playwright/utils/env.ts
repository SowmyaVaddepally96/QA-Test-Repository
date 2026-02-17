/**
 * Test environment and base URL.
 * Set BASE_URL when running against a deployed or local Sophi app.
 */
export const baseURL = process.env.BASE_URL || 'http://localhost:3000';

export const testUser = {
  valid: {
    email: process.env.TEST_USER_EMAIL || 'test@example.com',
    password: process.env.TEST_USER_PASSWORD || 'test-password',
  },
  restricted: {
    email: process.env.TEST_RESTRICTED_USER_EMAIL || 'restricted@example.com',
    password: process.env.TEST_RESTRICTED_USER_PASSWORD || 'test-password',
  },
};

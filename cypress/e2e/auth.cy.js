describe("Auth (Login / Sign Up)", () => {
  const uniqueEmail = () => `user_${Date.now()}@example.com`;

  it("1. Test Page Access: shows Login and Sign Up options", () => {
    cy.visit("/auth");
    cy.get('[data-cy="auth-options"]').within(() => {
      cy.get('[data-cy="auth-login-option"]').should("be.visible");
      cy.get('[data-cy="auth-signup-option"]').should("be.visible");
    });
  });

  it("2. Login Form Display: has email, password, login button", () => {
    cy.visit("/auth?mode=login");
    cy.get('[data-cy="login-form"]').within(() => {
      cy.get('[data-cy="login-email"]').should("exist");
      cy.get('[data-cy="login-password"]').should("exist");
      cy.get('[data-cy="login-submit"]').should("contain", "Login");
    });
  });

  it("3. Sign Up Form Display: has email, password, confirm, sign up button", () => {
    cy.visit("/auth?mode=signup");
    cy.get('[data-cy="signup-form"]').within(() => {
      cy.get('[data-cy="signup-email"]').should("exist");
      cy.get('[data-cy="signup-password"]').should("exist");
      cy.get('[data-cy="signup-confirm"]').should("exist");
      cy.get('[data-cy="signup-submit"]').should("contain", "Sign Up");
    });
  });

  it("4. Mandatory Field Validation: shows messages when required fields missing", () => {
    cy.visit("/auth?mode=login");
    cy.get('[data-cy="login-submit"]').click();
    cy.get('[data-cy="login-email-error"]').should("contain", "required");
    cy.get('[data-cy="login-password-error"]').should("contain", "required");

    cy.visit("/auth?mode=signup");
    cy.get('[data-cy="signup-submit"]').click();
    cy.get('[data-cy="signup-email-error"]').should("contain", "required");
    cy.get('[data-cy="signup-password-error"]').should("contain", "required");
    cy.get('[data-cy="signup-confirm-error"]').should("contain", "required");
  });

  it("7. Error Handling: mismatched passwords shows error", () => {
    cy.visit("/auth?mode=signup");
    cy.get('[data-cy="signup-email"]').type(uniqueEmail());
    cy.get('[data-cy="signup-password"]').type("password123");
    cy.get('[data-cy="signup-confirm"]').type("passwordXYZ");
    cy.get('[data-cy="signup-submit"]').click();
    cy.get('[data-cy="signup-confirm-error"]').should("contain", "match");
  });

  it("6. Successful Sign Up: creates account and redirects to products (auto-login)", () => {
    const email = uniqueEmail();
    cy.visit("/auth?mode=signup");
    cy.get('[data-cy="signup-email"]').type(email);
    cy.get('[data-cy="signup-password"]').type("password123");
    cy.get('[data-cy="signup-confirm"]').type("password123");
    cy.get('[data-cy="signup-submit"]').click();

    cy.url().should("include", "/products");
    cy.get('[data-cy="nav-user"]').should("contain", email);
  });

  it("5. Successful Login: logs in with valid credentials and redirects to products", () => {
    const email = uniqueEmail();

    // Sign up first
    cy.visit("/auth?mode=signup");
    cy.get('[data-cy="signup-email"]').type(email);
    cy.get('[data-cy="signup-password"]').type("password123");
    cy.get('[data-cy="signup-confirm"]').type("password123");
    cy.get('[data-cy="signup-submit"]').click();
    cy.get('[data-cy="nav-logout"]').click();

    // Now login
    cy.visit("/auth?mode=login");
    cy.get('[data-cy="login-email"]').type(email);
    cy.get('[data-cy="login-password"]').type("password123");
    cy.get('[data-cy="login-submit"]').click();

    cy.url().should("include", "/products");
    cy.get('[data-cy="nav-user"]').should("contain", email);
  });

  it("7. Error Handling: invalid credentials shows error message", () => {
    cy.visit("/auth?mode=login");
    cy.get('[data-cy="login-email"]').type("nope@example.com");
    cy.get('[data-cy="login-password"]').type("wrongpassword");
    cy.get('[data-cy="login-submit"]').click();
    cy.get('[data-cy="auth-error"]').should("contain", "Invalid credentials");
  });
});


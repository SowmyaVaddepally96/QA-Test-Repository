describe("BabyShop", () => {
  it("browses products and adds item to cart from listing", () => {
    cy.visit("/products");

    cy.get('[data-cy="page-title"]').should("contain", "Baby essentials");
    cy.get('[data-cy="product-card"]').should("have.length.greaterThan", 0);

    cy.get('[data-cy="nav-cart"]').click();
    cy.get('[data-cy="empty-cart"]').should("exist");

    cy.visit("/products");
    cy.get('[data-cy="product-card"]').first().within(() => {
      cy.get('[data-cy="add-to-cart"]').click();
    });

    cy.url().should("include", "/cart");
    cy.get('[data-cy="cart-row"]').should("have.length", 1);
    cy.get('[data-cy="cart-subtotal"]').should("contain", "Subtotal:");
    cy.get('[data-cy="cart-count"]').should("not.contain", "0");
  });

  it("searches for a product and opens product detail", () => {
    cy.visit("/products");

    cy.get('[data-cy="search-input"]').clear().type("bottle");
    cy.get('[data-cy="search-submit"]').click();

    cy.get('[data-cy="product-card"]').should("have.length.greaterThan", 0);
    cy.get('[data-cy="product-card"]').first().within(() => {
      cy.get('[data-cy="product-link"]').click();
    });

    cy.get('[data-cy="product-title"]').should("exist");
    cy.get('[data-cy="add-to-cart-detail"]').should("exist");
  });

  it("completes checkout and sees order confirmation", () => {
    cy.visit("/products");
    cy.get('[data-cy="product-card"]').first().within(() => {
      cy.get('[data-cy="add-to-cart"]').click();
    });

    cy.get('[data-cy="go-to-checkout"]').click();
    cy.url().should("include", "/checkout");

    cy.get('[data-cy="checkout-form"]').within(() => {
      cy.get('[data-cy="fullName"]').type("Alex Parent");
      cy.get('[data-cy="email"]').type("alex@example.com");
      cy.get('[data-cy="address"]').type("123 Baby St");
      cy.get('[data-cy="city"]').type("San Jose");
      cy.get('[data-cy="postalCode"]').type("95112");
      cy.get('[data-cy="place-order"]').click();
    });

    cy.url().should("include", "/order-confirmation");
    cy.get('[data-cy="confirmation-title"]').should("contain", "Order placed");
    cy.get('[data-cy="order-id"]').invoke("text").should("match", /^\d+$/);

    cy.get('[data-cy="nav-cart"]').click();
    cy.get('[data-cy="empty-cart"]').should("exist");
  });
});


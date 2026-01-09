/**
 * Cypress will load this config file in Node.
 *
 * Important: We intentionally avoid `require("cypress")` here so that
 * running Cypress via a globally installed Cypress app/binary works even
 * if the `cypress` npm package is not installed in this repo.
 */
module.exports = {
  e2e: {
    baseUrl: "http://localhost:8080",
    supportFile: false,
  },
};


# Playwright Test Writer Output: Sophi (Node 8062-9900)

**Source:** figma-test-case-discovery-sophi-node-8062-9900-normalized.md  
**Agent:** playwright-test-writer (playwright-cursor-agent)  
**Date:** 2026-02-17

---

## Summary

Playwright tests were generated from the **normalized test cases** (44 cases across UI Flow, Component State, Layout, Responsive, Accessibility, Error/Edge). All automation lives under **/playwright** as required.

- **Tests added:** Auth (3), Smoke (2), Plan of Care (6), Manage Employees (3), Manage Clients (1), Manage Schedule (2), Dashboard (4), Time Entry (1), Components (9), Forms validation (1), Layout (4), Accessibility (4).
- **Page objects:** LoginPage, DashboardPage, PlanOfCarePage, EmployeeListPage, ClientListPage, SchedulePage, TimeEntryPage.
- **Fixtures:** authFixture (loginPage, dashboardPage).
- **Selector strategy:** getByRole, getByLabel, getByText (no app in repo to discover data-testid).
- **Base URL:** `process.env.BASE_URL || 'http://localhost:3000'`. Set **BASE_URL** when running against the real Sophi app.

---

## Playwright Folder Structure

```
playwright/
  playwright.config.ts
  tsconfig.json
  tests/
    auth/
      login.spec.ts
    smoke/
      smoke.spec.ts
    regression/
      plan-of-care.spec.ts
      manage-employees.spec.ts
      manage-clients.spec.ts
      manage-schedule.spec.ts
      dashboard.spec.ts
      time-entry.spec.ts
      components.spec.ts
      forms-validation.spec.ts
      layout.spec.ts
      accessibility.spec.ts
  pages/
    LoginPage.ts
    DashboardPage.ts
    PlanOfCarePage.ts
    EmployeeListPage.ts
    ClientListPage.ts
    SchedulePage.ts
    TimeEntryPage.ts
  fixtures/
    authFixture.ts
  utils/
    env.ts
```

---

## Files Created / Updated

| File | Purpose |
|------|---------|
| playwright/playwright.config.ts | Config: baseURL from env, projects smoke/regression/auth, retries, trace/screenshot/video |
| playwright/tsconfig.json | TypeScript for Playwright |
| playwright/utils/env.ts | baseURL, testUser (valid + restricted) from env |
| playwright/pages/LoginPage.ts | Login flow, no-permission expectation |
| playwright/pages/DashboardPage.ts | Dashboard, Incident Forms, Background Check sections |
| playwright/pages/PlanOfCarePage.ts | PoC navigation, Client Overview, tabs, expandable, medical empty |
| playwright/pages/EmployeeListPage.ts | Manage Employees, Add Employee |
| playwright/pages/ClientListPage.ts | Manage Clients, Add Client |
| playwright/pages/SchedulePage.ts | Manage Schedule, Add Client Visit, calendar |
| playwright/pages/TimeEntryPage.ts | Time Entry, role-specific screens |
| playwright/fixtures/authFixture.ts | loginPage, dashboardPage fixtures |
| playwright/tests/auth/login.spec.ts | UI-1, UI-2, EE-1 |
| playwright/tests/smoke/smoke.spec.ts | Smoke subset |
| playwright/tests/regression/*.spec.ts | All regression and component/layout/a11y specs |

---

## Selector Sources

- **No Sophi app in this repo.** Selectors were inferred from the normalized test cases and common patterns (routes, labels, roles).
- **Priority used:** getByRole, getByLabel, getByText. data-testid was not available (app not in repo).
- **When the Sophi app is available:** Run the app locally, inspect DOM or component source for `data-testid`, and replace locators in page objects and specs. Prefer `data-testid` where present.

---

## Playwright Tests

Test files are under `playwright/tests/`. Mapping from normalized IDs:

| Normalized ID | Spec file |
|---------------|-----------|
| UI-1, UI-2, EE-1 | auth/login.spec.ts, smoke/smoke.spec.ts |
| UI-3, CS-8, CS-14, CS-15, EE-4, AX-4 | regression/plan-of-care.spec.ts |
| UI-4, CS-13, EE-6 | regression/manage-employees.spec.ts |
| UI-5, RS-4 | regression/manage-schedule.spec.ts |
| UI-6 | regression/manage-clients.spec.ts |
| UI-7 | regression/time-entry.spec.ts |
| UI-8, UI-9, EE-2, EE-3 | regression/dashboard.spec.ts |
| CS-1, CS-2, CS-5, CS-6, CS-9, CS-10, CS-11, CS-16, EE-7 | regression/components.spec.ts |
| EE-5 | regression/forms-validation.spec.ts |
| LV-1, LV-2, RS-2, RS-3 | regression/layout.spec.ts |
| AX-1, AX-2, AX-3, AX-5 | regression/accessibility.spec.ts |

---

## How to Run

1. **Install Playwright** (from repo root or playwright folder):
   ```bash
   npm install -D @playwright/test
   npx playwright install
   ```

2. **Set base URL** (when Sophi app is running):
   ```bash
   export BASE_URL=http://localhost:3000
   # Optional: test users
   export TEST_USER_EMAIL=test@example.com
   export TEST_USER_PASSWORD=...
   export TEST_RESTRICTED_USER_EMAIL=restricted@example.com
   export TEST_RESTRICTED_USER_PASSWORD=...
   ```

3. **Run all tests:**
   ```bash
   npx playwright test playwright/tests
   ```

4. **Run by project:**
   ```bash
   npx playwright test --project=smoke
   npx playwright test --project=regression
   npx playwright test --project=auth
   ```

5. **Run a single file:**
   ```bash
   npx playwright test playwright/tests/auth/login.spec.ts
   ```

6. **Debug:**
   ```bash
   npx playwright test playwright/tests --debug
   ```

---

## Notes / Assumptions

- **App not in repo:** The Sophi app (healthcare/care management) is not part of QA-Test-Repository. Tests are written to be **runnable once BASE_URL points to a running instance**. Selectors use roles/labels; update them after discovering real markup (and data-testid) from the app.
- **Routes:** Assumed routes: `/login`, `/dashboard`, `/plan-of-care`, `/manage-employees`, `/manage-clients`, `/manage-schedule`, `/time-entry`. Align with actual app routing.
- **Test users:** Valid and restricted users must exist (or be created via API) for UI-1, UI-2, EE-1. env.ts reads from env; replace with real credentials or API setup.
- **Conditional steps:** Some tests use `if (await locator.count() > 0)` where the UI might not exist on every page; they skip gracefully. Tighten when app structure is known.
- **AX-6, AX-7, AX-8:** Contrast and screen-reader checks are manual/axe; not implemented. Add `@axe-core/playwright` and axe assertions when needed.

---

*End of Playwright Test Writer Output*

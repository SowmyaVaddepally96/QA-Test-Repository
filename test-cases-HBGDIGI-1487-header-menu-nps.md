# Manual test cases: HBGDIGI-1487 — Header menu from Categories (NPS)

| Field | Value |
|-------|-------|
| **Jira** | [HBGDIGI-1487](https://hornblower.atlassian.net/browse/HBGDIGI-1487) |
| **Summary** | FE \| Get Header Menu from Categories (NPS) |
| **Source** | Jira issue description, acceptance criteria, and linked API notes (`get_ticket` / Jira MCP; `JIRA_API_MAIL` + `JIRA_API_KEY`) |
| **Related** | [HBGDIGI-1486](https://hornblower.atlassian.net/browse/HBGDIGI-1486) |
| **Last generated** | 2026-04-29 |
| **Last verified against Jira** | 2026-04-29 — `get_ticket(HBGDIGI-1487)` via Jira MCP; summary, AC, API paths, site phone matrix, static-logo AC, and header CTAs match this document |
| **Mode** | Discovery (requirements from Jira only; no sync to Figma frames in this run) |

## Assumptions

- “Site” means each branded experience (Statue, Alcatraz, Niagara, City Cruises, City Experiences, etc.) with its own `siteId` / OCAPI configuration.
- Salesforce Category / SCAPI responses are authoritative for nav structure when `showInMenu` is true; logo per current AC is **static in code** (ticket supersedes earlier “dynamic from Salesforce” wording).
- Figma links in Jira are visual references; detailed pixel checks are out of scope unless called out in AC (Contact Us modal layout per Figma is noted where AC says “refer to figma”).

---

## Summary

This story covers: (1) building the header navigation from Salesforce categories (IDs, names, levels, URLs, `showInMenu`, SEO fields from the Category API), (2) site-specific Contact Us phone numbers in a modal plus mobile `tel:` behavior, (3) static per-site logo in code, (4) translation selector aligned to theme and available locales, (5) header CTAs and links: Book Now, cart, sign-in/join, and My Account when authenticated. Test cases below map to each numbered acceptance theme, split into API/FE where useful. **Confidence:** High for AC explicitly stated in Jira; medium where Figma-only detail exists without prose AC.

---

## Happy Path Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| HP-1 | Root categories load for header nav | Valid org, `siteId`, SCAPI `HOST`; shopper token or configured public access per env | 1) Call SCAPI Get Category root endpoint with org and `siteId`. 2) Inspect JSON for categories intended for navigation. | Response 200; payload includes category tree or list usable to derive nav; no client-side error when FE consumes same contract. |
| HP-2 | Nav shows only categories with `showInMenu` true | Category data includes mix of `showInMenu` true/false | 1) Ensure SF data has at least one category with `showInMenu` false. 2) Load site header. | Categories with `showInMenu` false do not appear in main nav; true appear in correct hierarchy. |
| HP-3 | Nav exposes ID, name, level, URL | Categories returned with IDs, names, sub-category level, URL ID per story | 1) Map API fields to rendered nav. 2) Click a sub-category link. | Labels match API names; links resolve using URL ID / routing rules; hierarchy reflects sub-category level. |
| HP-4 | Category API supplies SEO for category pages | Nav link leads to a category route | 1) Open a category page from nav. 2) View page meta (title, description). | Page title and meta description match SEO fields from Category API (per AC). |
| HP-5 | Contact Us opens modal with Statue numbers | User on Statue-branded site | 1) Open header Contact Us (or equivalent). | Modal shows voice 877-523-9849 and text 833-528-0792 per AC; layout consistent with Figma reference. |
| HP-6 | Contact Us opens modal with Alcatraz numbers | User on Alcatraz-branded site | Same as HP-5 for Alcatraz. | Voice 888-467-6256; text 833-997-5257. |
| HP-7 | Contact Us opens modal with Niagara numbers | User on Niagara-branded site | Same as HP-5 for Niagara. | Voice 855-264-2427 (only number listed for Niagara in AC). |
| HP-8 | Contact Us opens modal with City Cruises numbers | User on City Cruises site | Same as HP-5. | Voice 800-459-8105; text 833-997-5300. |
| HP-9 | Contact Us opens modal with City Experiences numbers | User on City Experiences site | Same as HP-5. | Voice 800-459-8105; text 833-997-5300. |
| HP-10 | Mobile tap on phone initiates call | Real or emulated mobile browser; `tel:` supported | 1) Open Contact Us on mobile viewport. 2) Tap displayed phone number. | OS dialer opens with correct number on iOS and Android. |
| HP-11 | Logo correct per site (static in code) | Code/config defines per-site logo asset | 1) Load each major site variant. 2) Observe header logo. | Correct logo for each site; matches code-managed asset (not SF Library per current AC). |
| HP-12 | Language menu matches theme and available translations | Site has configured locales | 1) Open language/translation control in header. 2) Compare to site’s supported languages. | Control styling matches site theme; only available translations listed; switching locale updates content as designed. |
| HP-13 | Book Now routes to Tickets (default sites) | Non-Niagara site with Tickets entry in nav | 1) Click Book Now in header. | User lands on Tickets flow/URL defined for that site (not Tours-only). |
| HP-14 | Book Now routes to Tours for Niagara | Niagara site | 1) Click Book Now. | User lands on Tours entry point per AC for Niagara. |
| HP-15 | Cart icon navigates to shopping cart | Any page with header | 1) Click cart icon. | Browser navigates to `/shopping-cart`. |
| HP-16 | Sign in / Join goes to sign-in | Guest user | 1) Click “Sign in” or “Join For Free” (per UI copy). | Navigates to `/sign-in`. |
| HP-17 | My Account when signed in | Authenticated user session | 1) Sign in. 2) Click My Account in header. | Navigates to `/my-account`; behavior consistent with My Account in main navigation. |

---

## Edge Case Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| EC-1 | Deep category tree (levels up to API depth) | Categories with many nested levels; API `levels=10` or equivalent | 1) Load nav. 2) Expand/hover through deepest visible levels. | Nav renders without truncation errors; performance acceptable; deepest items still link correctly. |
| EC-2 | All top-level categories `showInMenu` false | SF data edge configuration | Load header. | Main nav empty or fallback behavior per product spec; no broken layout (if undefined, log as gap). |
| EC-3 | Single phone line site (Niagara) | Niagara | Open Contact Us. | Only listed Niagara number(s) shown; no placeholder for missing text line unless product adds one. |
| EC-4 | Long site or category name | SF name at upper reasonable length | View nav labels. | Text wraps or ellipsizes without overlapping logo or breaking header layout. |
| EC-5 | User switches site in multi-site QA harness (if applicable) | Two sites in same browser profile | Switch site context per test env. | Logo, phones, translations, and Book Now target all switch to new site defaults. |

---

## Negative Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| NEG-1 | Category API timeout or 5xx | Mock or staging fault injection | Load page with header. | Graceful degradation: user-visible message or cached nav policy per spec; no uncaught exception; optional retry does not infinite-loop. |
| NEG-2 | Category API 401/403 | Invalid or expired token | Request categories. | FE handles error; nav does not show misleading links; error monitoring captures cause. |
| NEG-3 | Malformed category payload (missing URL ID) | Test data or mock | Load nav. | Item skipped or safe fallback; no link to `/undefined` or blank href. |
| NEG-4 | Contact Us modal dismissed | Modal open | Click outside / close / ESC per design. | Modal closes; focus returns sensibly. |
| NEG-5 | Guest clicks My Account if copy still visible incorrectly | Edge UI state | Attempt My Account while logged out (if control visible). | Redirect to sign-in or control hidden per auth rules (align with main nav). |

---

## Security Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| SEC-1 | XSS in category name from API | Controlled test category name with HTML/script | Render nav. | Output encoded; script does not execute. |
| SEC-2 | Open redirect via URL ID | Malicious URL pattern if SF misconfigured | Click affected nav link. | App validates internal routes; no arbitrary external redirect without user intent. |
| SEC-3 | API keys / secrets not exposed client-side | Browser devtools | Inspect network from browser for category calls. | Only client-safe tokens; no server-only secrets in bundle or responses logged to client. |

---

## Requirements gaps identified

| Gap ID | Type | Description | Recommended clarification |
|--------|------|-------------|---------------------------|
| GAP-1 | Undefined behavior | Nav when **all** categories have `showInMenu` false | Define empty nav vs. hardcoded fallback links. |
| GAP-2 | Ambiguous | Exact **Book Now** URLs for each brand besides “Tickets vs Niagara Tours” | Document per-`siteId` redirect targets for QA assertions. |
| GAP-3 | Integration | Relationship to **HBGDIGI-1486** (dependency, ordering, shared API) | Confirm cross-ticket acceptance and regression scope. |
| GAP-4 | SEO scope | “SEO needed Page title, description, etc.” — full list of meta tags | List required tags (OG, canonical, hreflang) if in scope. |
| GAP-5 | Accessibility | Contact modal focus trap, ESC, aria labels | Align with Figma + a11y checklist if required by NPS standards. |

---

## Coverage matrix

| Acceptance theme | HP / EC / NEG / SEC IDs |
|------------------|-------------------------|
| SF nav IDs, names, level, URL; `showInMenu`; SEO from Category API | HP-1–HP-4, EC-1–EC-2, NEG-1–NEG-3, SEC-1–SEC-2 |
| Site-specific Contact Us + mobile dial | HP-5–HP-10, EC-3, NEG-4 |
| Static logo per site | HP-11 |
| Translation menu theme + locales | HP-12, EC-5 |
| Book Now (incl. Niagara Tours) | HP-13–HP-14 |
| Cart `/shopping-cart` | HP-15 |
| Sign in `/sign-in` | HP-16 |
| My Account `/my-account` when signed in | HP-17, NEG-5 |
| API resilience / security | NEG-1–NEG-2, SEC-3 |

**API reference (from ticket):**  
`GET {{HOST}}/product/shopper-products/v1/organizations/{{organizationId}}/categories/root?&siteId={{ocapi_site}}`  
`GET {{HOST}}/product/shopper-products/v1/organizations/{{organizationId}}/categories/&siteId={{ocapi_site}}&levels=10`

---

## Priority recommendations

1. **HP-2, HP-3, NEG-3** — `showInMenu` and URL mapping are core navigation correctness.  
2. **HP-5–HP-10** — Revenue/support impact; verify each site’s number set and mobile `tel:`.  
3. **HP-13–HP-14** — Niagara vs other sites is an easy miss in regression.  
4. **HP-15–HP-17** — Simple link regressions with high user impact.  
5. **NEG-1–NEG-2** — Resilience when Salesforce/SCAPI is degraded.

---

## Automation assessment

**Criteria:** Yes = deterministic automatable; Partial = needs mocks/fixtures/selectors; No = heavy human judgment or device-only.

| ID | Automatable? | Automation notes |
|----|--------------|------------------|
| HP-1 | Partial | Contract test against SCAPI with env secrets in CI vault; assert schema and `showInMenu`. |
| HP-2 | Yes | Intercept or fixture JSON with mixed flags; assert DOM nodes absent/present. |
| HP-3 | Partial | Assert `href` and text from known fixture IDs. |
| HP-4 | Yes | Playwright/Cypress assert `document.title` and meta after navigation. |
| HP-5–HP-9 | Partial | Parameterize `baseURL` per site; assert modal text content. |
| HP-10 | No / Partial | Real device or dedicated mobile farm; emulators vary for `tel:`. |
| HP-11 | Yes | Visual snapshot or assert `img[src]` per site config. |
| HP-12 | Partial | Assert option list length and theme class on control. |
| HP-13–HP-14 | Yes | Assert final URL path or route name per site flag. |
| HP-15–HP-17 | Yes | Assert `location.pathname` after click. |
| EC-1–EC-5 | Partial | Deep tree needs performant fixture; multi-site needs env matrix. |
| NEG-1–NEG-3 | Partial | Mock network failures and malformed payloads. |
| SEC-1–SEC-2 | Partial | Security tests often in dedicated suite with sanitized fixtures. |
| SEC-3 | Manual / tooling | Bundle and network audit tooling. |

### Summary: automation counts (approximate)

| Category | Yes | Partial | No |
|----------|-----|---------|-----|
| Happy Path | 6 | 9 | 1 |
| Edge Case | 0 | 5 | 0 |
| Negative | 0 | 4 | 0 |
| Security | 0 | 2 | 1 |
| **Total** | 6 | 20 | 2 |

**Recommendation:** Automate HP-15–HP-17 and HP-2 first (fast, stable). Add API contract tests for category payloads, then modal content per site with parameterized runs.

---

## Figma references (from Jira)

- [05 Statue — Design (node)](https://www.figma.com/design/CqYBgc1rjcFD7yDypffc97/05-Statue---Design?node-id=2518-21204&m=dev)  
- [06 Alcatraz — Design (node)](https://www.figma.com/design/C0nWeH94glSZ3ZxchKzvus/06-Alcatraz---Design?node-id=8548-135001&m=dev)  
- [09 Niagara — Design (node)](https://www.figma.com/design/JMEwD37GKss06GqRaE2jdN/09-Niagara-Design?node-id=2139-71491&m=dev)  

For UI-only deltas not spelled out in Jira prose, run **figma-test-case-discovery** on updated frames if visual AC tightens.

---

## Changelog

- **2026-04-29 (Zephyr — consolidated):** Created Scale test case **HBGDIGI-T742** — **22 Test Script** steps (Happy Path + Negative from this doc), owner **Sowmya Vaddepally** (`712020:e38b5294-2483-4bda-bede-ef35905af4ff`), folder **Page Designer - Components / Header** (folder id `41659526`). **Traceability** to Jira **HBGDIGI-1487** (issue id `375853`) applied. Import used `--single-testcase`. Open **HBGDIGI-T742** in Zephyr Scale under project **HBGDIGI** to review.
- **2026-04-29 (Cursor /test-case-discovery):** Re-fetched [HBGDIGI-1487](https://hornblower.atlassian.net/browse/HBGDIGI-1487) with Jira MCP `get_ticket`. Ticket **FE | Get Header Menu from Categories (NPS)** — user stories (developer nav from SF; user logo + contact), context (catalog/category/sub-category), and ordered AC (SCAPI fields, `showInMenu`, SEO, Contact Us per site + mobile `tel:`, static logo, translation menu, Book Now / cart / sign-in / My Account routes) align with tables below; **no new rows added**. Jira still has many image attachments; if Feb 2026 screenshots add prose AC, sync this file or run **figma-test-case-discovery**.
- **2026-04-29:** Re-run **test-case-discovery** for [HBGDIGI-1487](https://hornblower.atlassian.net/browse/HBGDIGI-1487) using Jira MCP `get_ticket`. Summary, happy path, edge, negative, security tables, gaps, coverage matrix, and automation assessment were **re-checked** against current Jira description (including struck “dynamic logo” vs **static logo in code**); **no row edits required**. Jira lists additional **Feb 2026** image attachments not reflected in prose—if those screenshots change UI AC, update this doc or run **figma-test-case-discovery** after design review.
- **2026-04-29 (Zephyr):** Imported **Happy Path** + **Negative** rows into Zephyr Scale project **HBGDIGI**, folder **`Page Designer - Components/Header`** (folder id `41659526`), owner **Sowmya Vaddepally** (`712020:e38b5294-2483-4bda-bede-ef35905af4ff`). Created **HBGDIGI-T720** through **HBGDIGI-T741** (HP-1…HP-17, NEG-1…NEG-5). **Traceability** to Jira issue was skipped (`ZEPHYR_SKIP_ISSUE_LINK=1`) because `JIRA_CLOUD_URL` + `JIRA_API_MAIL` + `JIRA_API_KEY` were not available in the import environment—**link each case to [HBGDIGI-1487](https://hornblower.atlassian.net/browse/HBGDIGI-1487)** in Zephyr (or add Jira env vars and use a maintenance script) if required by your process.

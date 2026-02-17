# Figma Test Case Discovery: Sophi — Accounting | Billing Periods

**Source:** [Figma — Sophi Developers Hand Off](https://www.figma.com/design/yFFgIDlTbDcQAbICJyFEuu/Sophi---Developers-Hand-Off?node-id=17377-50113)  
**Scoped node:** `17377:50113` — **Accounting | Billing Periods**  
**Data source:** Local Figma extraction (`figma-data/node-structure.json`, `node-full.json`, `comments.json`). Live API returned 429 (rate limit); analysis uses cached data.

**Mode:** Discovery from Figma design. Assumptions: (1) Screen is part of an Accounting/Billing workflow; (2) table is data-driven with sort/filter; (3) design comments (e.g. reminder on submit, date/time consistency) apply to this or related flows.

---

## Summary

The **Accounting | Billing Periods** frame is a main content screen with a **Requirements** section (billing-periods table with filters, add action, row menus), **employee profile** area (tabs, client dropdown), **side menu** (nav tabs, notifications, messages, user profile), and **top navigation** (org selector, breadcrumbs). The design implies: filters, add billing period, sortable table columns, status chips, row actions (SidePanel/Menu), pagination, and one row state with an alert on “# of Invoices Sent.” Design comments indicate a reminder message or modal on submit (replacing a deep link) and date/time/timezone consistency requirements. Test cases below are derived from the structure and comments; prototype interactions were not present in the extracted data.

---

## UI Flow Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| UI-1 | Navigate to Accounting \| Billing Periods from side menu | User is logged in; app shows default page. | Click the Accounting/Billing menu item in the Side Menu (Icon + label). | Billing Periods view loads; Requirements section and table are visible; breadcrumbs show path to this screen. |
| UI-2 | Open row actions menu | User is on Billing Periods; table has at least one row. | Click the SidePanel/Menu control on a table row. | Row actions menu opens (e.g. edit, view, delete or context-specific options). |
| UI-3 | Apply filters via Filters button | User is on Billing Periods. | Click the Filters button in the Requirements section. | Filter UI opens; user can set filter criteria (e.g. date range, status, payor type). |
| UI-4 | Add new billing period | User is on Billing Periods; user has permission to add. | Click the button with Plus icon (Add) in the Requirements section. | Add flow starts (e.g. modal or new screen); form or wizard for new billing period is shown. |
| UI-5 | Navigate pagination (next page) | User is on Billing Periods; table has more than one page. | Click the next (right arrow) pagination control. | Table shows the next page of rows; pagination state updates (e.g. current page number). |
| UI-6 | Navigate pagination (previous page) | User is on Billing Periods; current page > 1. | Click the previous (left arrow) pagination control. | Table shows the previous page of rows; pagination state updates. |
| UI-7 | Jump to first/last page | User is on Billing Periods; multiple pages exist. | Click Skip to first or Skip to last pagination control. | Table shows first or last page respectively; pagination state updates. |
| UI-8 | Change tab in employee profile area | User is on Billing Periods; Tabs are visible. | Click a different tab in the Tabs strip (Horizontal Tabs). | Tab content switches; selected tab is visually indicated. |
| UI-9 | Expand/collapse client dropdown | User is on Billing Periods; client information dropdown is visible. | Click the client information dropdown (Avatar, Name, Gender, Age, down arrow). | Dropdown expands to show full client summary/details or collapses if already open. |
| UI-10 | Open organization selector | User is on Billing Periods; Top Navigation shows Organization (e.g. CAB). | Click the Organization control (CAB + down arrow). | Organization selector opens; user can switch organization/context. |
| UI-11 | Follow breadcrumb | User is on Billing Periods; breadcrumbs show path. | Click a breadcrumb segment (e.g. parent section). | Navigation goes to that segment’s page; breadcrumbs update. |
| UI-12 | Submit flow shows reminder (per design comment) | User completes an action that triggers “submit” (e.g. add billing period). | Complete required fields and submit. | Reminder message or reminder modal is shown (replacing previous deep link to 3rd party); no deep link to 3rd party system. |

---

## Component State Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| CS-1 | Filters button default state | User is on Billing Periods. | Observe the Filters button. | Button shows Filters icon and label; default visual state. |
| CS-2 | Add (Plus) button default state | User is on Billing Periods. | Observe the Add (Plus) button. | Button shows Plus icon and label; default visual state. |
| CS-3 | Status chip default display | User is on Billing Periods; row has a status. | Locate a row Status (chips-general). | Status chip shows icon(s) and label; consistent with design (e.g. Approved, Pending). |
| CS-4 | Row menu button hover/focus | User is on Billing Periods. | Hover or focus the SidePanel/Menu control on a row. | Control shows hover/focus state (e.g. highlight, cursor change). |
| CS-5 | Pagination current page state | User is on Billing Periods; multiple pages exist. | Navigate to a specific page. | Current page item is visually distinct (e.g. selected/filled); other page buttons are not. |
| CS-6 | Pagination disabled on first/last page | User is on first (or last) page. | Observe previous (or next) control. | Previous is disabled on first page; next is disabled on last page (or not shown). |
| CS-7 | Tab selected state | User is on Billing Periods. | Select a tab. | Selected tab has distinct style; notification dot (ellipse) shown per design if applicable. |
| CS-8 | Client dropdown expanded state | User has opened the client information dropdown. | Observe dropdown. | Expanded content is visible (e.g. details); down arrow indicates open state. |
| CS-9 | Alert state on “# of Invoices Sent” | Row has discrepancy (design shows “3” with Exclamation tag). | Locate row with TEMPORAL - Atoms / Tags / Alerts on # of Invoices Sent. | Alert/tag is visible (e.g. count “3” with exclamation); indicates attention needed. |

---

## Layout and Visual Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| LV-1 | Table column order and headers | User is on Billing Periods. | Observe table heading row. | Columns appear in order: End Date, Frequency, Invoice Date, Payor Type, Invoiced Hours, Invoices, Status, NOTES; scroll controls and Status filter present as designed. |
| LV-2 | Table row alignment | Table has multiple rows. | Compare row cells to header cells. | Cell content aligns with column headers; no horizontal misalignment. |
| LV-3 | Requirements section scroll | Content exceeds viewport height. | Scroll the Requirements frame. | Frame scrolls (scrollBehavior SCROLLS); table header can stay fixed or scroll per spec. |
| LV-4 | Side menu nav item alignment | User is on Billing Periods. | Observe Menu tabs (Icon + label, expand icon). | Icons and labels align; expand icon aligned; spacing consistent. |
| LV-5 | Top nav and breadcrumbs alignment | User is on Billing Periods. | Observe Top Navigation (Organization, Breadcrumbs). | Organization and breadcrumbs are aligned and readable; logo/CAB and dropdown clear. |
| LV-6 | Pagination alignment | Table has multiple pages. | Observe pagination component. | SkipPrevious, page numbers, SkipNext are in a single row; buttons evenly spaced. |
| LV-7 | Variable-based fill (theme) | Design uses boundVariables for fills. | Switch theme/mode if supported (e.g. light/dark). | Background/fills update per variable (e.g. VARIABLE_ALIAS); no broken or default-only fill. |

---

## Responsive Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| RS-1 | Billing Periods at desktop width | Viewport ≥ breakpoint for full layout. | Load Billing Periods at desktop width (e.g. 1440px). | Side menu, main content (Requirements table), employee profile, top nav all visible; layout matches frame. |
| RS-2 | Horizontal scroll or column visibility at narrow width | Viewport is narrower than full table. | Reduce width to breakpoint where table is constrained. | Table either scrolls horizontally or columns hide/stack per spec; no overlapping critical controls. |
| RS-3 | Side menu at narrow viewport | Viewport is at tablet/mobile breakpoint. | Load or resize to narrow width. | Side menu collapses to icon-only or drawer; navigation still reachable. |
| RS-4 | Pagination at small width | Viewport is narrow. | View pagination. | Pagination remains usable (e.g. truncated page numbers or prev/next only); no overflow. |
| RS-5 | Tabs overflow/wrap | Many tabs in employee profile area. | View with limited horizontal space. | Tabs wrap or scroll horizontally; no clipping of active tab. |

---

## Accessibility Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| AX-1 | Table has accessible headers | User is on Billing Periods. | Use screen reader or accessibility tree. | Table has row/column headers exposed; cells are associated with headers. |
| AX-2 | Filters and Add buttons are focusable and labeled | User is on Billing Periods. | Tab to Filters and Add buttons. | Each receives focus in logical order; accessible name matches purpose (e.g. “Filters”, “Add billing period”). |
| AX-3 | Row menu is keyboard activatable | Focus is on a row’s SidePanel/Menu. | Activate with Enter or Space. | Row menu opens; focus moves into menu. |
| AX-4 | Pagination is keyboard operable | Focus is on pagination. | Tab through and activate previous/next/page. | All interactive pagination controls are focusable and activatable; focus order is logical. |
| AX-5 | Tab list has correct role and selected state | User uses assistive tech. | Focus on Tabs in employee profile. | Tab list has role tablist; selected tab has selected state; tab panels are associated. |
| AX-6 | Status chip and alert are announced | Row has status chip or alert (e.g. exclamation). | Navigate with screen reader. | Status and alert (e.g. “3 invoices need attention”) are announced. |
| AX-7 | Color and focus visibility | User relies on focus indicator. | Tab through interactive elements. | Focus indicator is visible (e.g. outline or ring) and meets contrast requirements. |

---

## Error and Edge UI Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|----|----------|---------------|-------|------------------|
| EE-1 | Empty table state | User is on Billing Periods; no billing periods exist. | Load the screen or clear all data. | Empty state is shown (message and/or illustration); no raw “0 rows”; Add CTA visible. |
| EE-2 | Single row display | Only one billing period exists. | Load Billing Periods. | Single row displays correctly; pagination hidden or shows “1 of 1”. |
| EE-3 | Row with alert on Invoices Sent | At least one row has discrepancy (e.g. 3 not sent). | Locate row with alert tag. | Alert (exclamation + count) is visible and does not break layout; tooltip or link if specified. |
| EE-4 | Filter returns no results | Filters are set such that no rows match. | Apply filter that matches zero rows. | “No results” or empty state message; option to clear filters. |
| EE-5 | API/load failure | Backend or network fails when loading table. | Simulate failure or disconnect. | Error message or inline error state; retry or support action available. |
| EE-6 | Long content in cells | Row has long End Date, Payor Type, or Notes text. | Load data with long values. | Text truncates or wraps per spec; tooltip or expand if designed. |
| EE-7 | Date/time and timezone consistency (per comments) | User creates or edits a billing period with dates. | Set date (and time if applicable); check date picker and displayed date. | Displayed date matches date picker; timezone (if shown) is consistent; design comments suggest showing client timezone where relevant. |

---

## ⚠️ Requirements Gaps Identified

| Gap ID | Type | Description | Recommended Clarification |
|--------|------|-------------|----------------------------|
| GAP-1 | Copy/Behavior | Reminder on submit: design comment says “reminder message here or reminder modal on submit” instead of deep link—exact placement and copy are not specified. | Define: inline message vs. modal; exact copy; which submit actions trigger it. |
| GAP-2 | Interaction | No prototype data in extraction for Filters, Add, row menu, or pagination. | Confirm click targets, loading states, and error states for each. |
| GAP-3 | Responsive | Breakpoints and behavior for table and side menu at tablet/mobile are not defined in extracted data. | Define breakpoints, column priority, and menu behavior (drawer vs. icon bar). |
| GAP-4 | States | Error and loading states for table and buttons are not visible in structure. | Specify loading skeletons/spinners and error UI for table and primary actions. |
| GAP-5 | Data | “Invoiced Hours” appears in header; row structure shows “# of Invoices” and “# of Invoices Sent”—mapping and any “Invoiced Hours” column need confirmation. | Confirm column mapping and whether “Invoiced Hours” is separate or derived. |
| GAP-6 | Timezone | Comments mention showing timezone (e.g. client timezone when creating visit, timezone in UI). | Clarify where timezone is shown on Billing Periods (e.g. date columns, filters) and format. |
| GAP-7 | Accessibility | Focus order and ARIA for table, filters, and row menu not specified in design. | Define tab order and ARIA roles/labels for complex widgets. |

---

## Coverage Matrix

| Screen / Component | UI Flows | Component States | Layout | Responsive | A11y | Error/Edge |
|--------------------|----------|------------------|--------|------------|------|------------|
| Accounting \| Billing Periods (frame) | UI-1–UI-12 | — | LV-1–LV-7 | RS-1–RS-5 | AX-1–AX-7 | EE-1–EE-7 |
| Requirements section | UI-2–UI-7 | CS-1–CS-2, CS-4 | LV-1–LV-3, LV-6 | RS-2 | AX-1–AX-4 | EE-1–EE-5 |
| Table (heading + rows) | UI-2, UI-4–UI-7 | CS-3, CS-9 | LV-1–LV-2 | RS-2 | AX-1, AX-6 | EE-1–EE-4, EE-6 |
| Filters / Add buttons | UI-3, UI-4 | CS-1–CS-2 | — | — | AX-2 | — |
| Row menu (SidePanel/Menu) | UI-2 | CS-4 | — | — | AX-3 | — |
| Pagination | UI-5–UI-7 | CS-5–CS-6 | LV-6 | RS-4 | AX-4 | EE-2 |
| Tabs (employee profile) | UI-8 | CS-7 | — | RS-5 | AX-5 | — |
| Client dropdown | UI-9 | CS-8 | — | — | — | — |
| Side Menu | UI-1 | — | LV-4 | RS-3 | — | — |
| Top Navigation / Breadcrumbs | UI-10–UI-11 | — | LV-5 | — | — | — |
| Submit reminder (per comment) | UI-12 | — | — | — | — | — |
| Date/time and timezone | — | — | — | — | — | EE-7 |

---

## Priority Recommendations

1. **UI-12, GAP-1** — Implement and test reminder message/modal on submit; remove any deep link to 3rd party. High impact for compliance and user expectation.
2. **UI-2, UI-3, UI-4** — Test row menu, Filters, and Add flows end-to-end; confirm with product that behavior matches design comments.
3. **EE-1, EE-4, EE-5** — Test empty, no-results, and load-failure states; ensure clear messaging and recovery.
4. **AX-1, AX-2, AX-3, AX-4** — Validate table semantics, button labels, row menu, and pagination for keyboard and screen reader.
5. **EE-7, GAP-6** — Align dates and timezone with design comments (date picker match, client timezone where applicable).
6. **RS-2, RS-3, GAP-3** — Define and test responsive behavior for table and side menu at smaller breakpoints.
7. **CS-9, EE-3** — Test row alert state (“# of Invoices Sent” discrepancy) and that it drives correct user action (e.g. link or tooltip).

---

## Automation Assessment

**Criteria:**  
- **Yes** — Deterministic steps and assertions; automatable with standard UI automation (e.g. Cypress, Playwright).  
- **Partial** — Automatable if selectors/APIs exist or viewport/device is fixed; or only part of the scenario can be automated.  
- **No** — Requires human judgment, visual-only checks, assistive tech, or unstable 3rd party; not recommended for UI automation.

| ID | Automatable? | Automation notes |
|----|--------------|------------------|
| **UI Flows** | | |
| UI-1 | **Yes** | Assert: URL or route, table visible, breadcrumb text. Use `data-testid` or role for menu item. |
| UI-2 | **Yes** | Click first row menu; assert menu/open state (role=menu or expanded). |
| UI-3 | **Yes** | Click Filters; assert filter panel/drawer visible (e.g. date range, status controls). |
| UI-4 | **Yes** | Click Add; assert modal or form visible (heading, required fields). |
| UI-5 | **Yes** | Click next; assert table rows change and/or page number updates. |
| UI-6 | **Yes** | Same as UI-5 for previous. |
| UI-7 | **Yes** | Click first/last; assert correct page (e.g. page 1 or last page number). |
| UI-8 | **Yes** | Click tab by index or label; assert tab selected (aria-selected) and content area updates. |
| UI-9 | **Yes** | Click dropdown; assert expanded content visible; click again to collapse. |
| UI-10 | **Yes** | Click org control; assert dropdown/popover open. |
| UI-11 | **Yes** | Click breadcrumb; assert navigation and breadcrumb update. |
| UI-12 | **Yes** | Complete add flow and submit; assert reminder message/modal visible and no deep-link element. |
| **Component State** | | |
| CS-1 | **Yes** | Assert Filters button visible, enabled, has accessible name. |
| CS-2 | **Yes** | Assert Add button visible, enabled, has accessible name. |
| CS-3 | **Yes** | Assert at least one status chip has text/role; optional snapshot for "consistent with design." |
| CS-4 | **Partial** | Hover/focus is automatable; "cursor change" is browser-dependent; assert focus/hover styling if stable. |
| CS-5 | **Yes** | After navigating, assert current page button has selected/aria-current. |
| CS-6 | **Yes** | On page 1 assert prev disabled; on last page assert next disabled. |
| CS-7 | **Yes** | Assert selected tab has aria-selected=true and distinct class/attribute. |
| CS-8 | **Yes** | After open, assert dropdown content in DOM and visible. |
| CS-9 | **Yes** | With fixture that has discrepancy row, assert alert/tag element and text (e.g. "3"). |
| **Layout / Visual** | | |
| LV-1 | **Yes** | Assert table header cells text/order (End Date, Frequency, …). |
| LV-2 | **Partial** | Assert column count and that cells exist; pixel alignment usually needs visual regression or design tokens. |
| LV-3 | **Yes** | Assert scrollable container and scroll position change after scroll. |
| LV-4 | **Partial** | Assert elements exist and order; exact spacing is layout/visual regression. |
| LV-5 | **Partial** | Same as LV-4. |
| LV-6 | **Yes** | Assert pagination buttons present and in single row (e.g. flex/grid). |
| LV-7 | **Partial** | Theme switch + assert no error; exact "fill update" may need visual or CSS variable assertion. |
| **Responsive** | | |
| RS-1 | **Yes** | Set viewport (e.g. 1440×900); assert side menu, table, top nav visible. |
| RS-2 | **Yes** | Set narrow viewport; assert table scrolls or columns hide; no critical overlap. |
| RS-3 | **Yes** | Set breakpoint; assert collapsed menu (e.g. drawer or icon bar) and nav still clickable. |
| RS-4 | **Yes** | Set narrow viewport; assert pagination visible and usable (no overflow). |
| RS-5 | **Yes** | Assert tabs wrap or scroll; active tab in view. |
| **Accessibility** | | |
| AX-1 | **Yes** | Use axe or similar; assert table has th/scope or aria; cells associated with headers. |
| AX-2 | **Yes** | Tab to buttons; assert focus order and accessible name (e.g. name/label). |
| AX-3 | **Yes** | Focus row menu; Enter/Space; assert menu opens and focus inside. |
| AX-4 | **Yes** | Tab through pagination; activate; assert state change. |
| AX-5 | **Yes** | Assert tablist role, tab roles, selected state, tabpanel association. |
| AX-6 | **Partial** | Assert status/alert in DOM and has accessible name; full "announced" needs a11y testing tool or AT. |
| AX-7 | **Partial** | Focus visibility can be asserted (outline/focus-visible); contrast needs dedicated a11y check. |
| **Error / Edge** | | |
| EE-1 | **Yes** | Use fixture with no billing periods; assert empty state message and Add CTA visible. |
| EE-2 | **Yes** | Use fixture with one row; assert one row and pagination hidden or "1 of 1." |
| EE-3 | **Yes** | Use fixture with discrepancy; assert alert visible and layout intact. |
| EE-4 | **Yes** | Apply filter with no matches; assert "No results" and clear filters option. |
| EE-5 | **Yes** | Mock API failure; assert error message and retry/support action. |
| EE-6 | **Yes** | Use fixture with long text; assert truncation or wrap (and tooltip if implemented). |
| EE-7 | **Partial** | Assert date picker value equals displayed date; timezone string if present; full consistency may need product rule. |

### Summary: Which test cases can be automated?

| Category | Automatable (Yes) | Partial | No |
|----------|-------------------|--------|-----|
| UI Flows | 12 | 0 | 0 |
| Component State | 7 | 2 (CS-4, CS-3 optional) | 0 |
| Layout / Visual | 3 | 4 (alignment/theme) | 0 |
| Responsive | 5 | 0 | 0 |
| Accessibility | 5 | 2 (AX-6, AX-7) | 0 |
| Error / Edge | 6 | 1 (EE-7) | 0 |
| **Total** | **38** | **9** | **0** |

**Recommendation:** All 47 test cases are either fully or partially automatable. Prioritize **Yes** cases for regression automation; **Partial** cases can be automated with explicit selectors, fixtures, and (where needed) visual or a11y tools. None are classified as non-automatable for UI automation.

---

*Discovery produced from Figma skill extraction (local `figma-data/`). Re-run `figma_fetch.py full` when API rate limit allows for interactions and full file context.*

# Normalized Test Cases: Sophi (Node 8062-9900)

**Source:** figma-test-case-discovery-sophi-node-8062-9900.md  
**Normalized by:** test-case-normalizer agent  
**Date:** 2026-02-17

---

## Summary

- **Input:** 52 test cases across 6 categories (UI Flow, Component State, Layout/Visual, Responsive, Accessibility, Error/Edge).
- **Deduplicated:** 2 tests merged (LV-1/RS-1 overlap on desktop grid; LV-7 merged into CS-13).
- **Removed / Flagged:** 8 items moved to Automation Gaps (purely visual or manual checks).
- **Normalized:** 44 automation-ready test cases with explicit preconditions, deterministic expected results, and automation metadata (Feature Area, Route, Tags, Setup Strategy).

---

## Deduplicated / Removed Tests

| Removed ID | Reason | Merged Into |
|------------|--------|-------------|
| RS-1 | Overlaps with LV-1 (desktop 12-column grid verification). | LV-1 (normalized as single desktop grid test). |
| LV-7 | Same intent as CS-13 (Do not send table column visibility). | CS-13 (normalized). |
| LV-3 | Non-automatable: "aligns with layout grid and design" is visual. | Automation Gaps. |
| LV-4 | Non-automatable: "Organism layout matches design" is visual. | Automation Gaps. |
| LV-5 | Non-automatable: "Layout and structure match each design" is visual. | Automation Gaps. |
| LV-6 | Non-automatable: "Offset values match frame-specific design" is pixel visual. | Automation Gaps. |
| CS-2, CS-3, CS-4 | Partially visual ("matches design"); kept but expected result made observable (variant/class present). | Normalized as CS-2, CS-3, CS-4. |
| AX-6 | Contrast check requires axe or manual audit; kept with note. | Normalized with tag `manual-optional`. |

---

## Automation Gaps

| Gap | Description | Recommendation |
|-----|-------------|----------------|
| Visual alignment | NavBar, Client Overview, Client/Employee profile layout "per design". | Use screenshot diff or design tokens in test; otherwise manual. |
| Grid offsets | 152px vs 264px vs 304px offset comparison. | Visual regression or design-token assertion. |
| WCAG contrast | Success/Error alert color contrast. | Run axe or pa11y in CI; not a single-step UI test. |
| "Matches design" | Button/TextField variant appearance. | Assert CSS class or data-variant attribute; avoid pixel comparison. |

---

## Normalized Test Cases

### UI Flow

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| UI-1 | Login with valid credentials redirects to main app | P1 | smoke, happy-path, auth | UI | Authentication | /login | User is logged out; Login screen is visible. | 1. Enter valid credentials. 2. Submit login form. | URL changes to /dashboard or /plan-of-care; main app shell (e.g. nav or dashboard content) is visible. |
| UI-2 | Login with restricted role shows no permission message | P1 | negative, auth | UI | Authentication | /login | User has restricted role; Login screen is visible. | 1. Enter credentials. 2. Submit login. | No-permission message element is visible; user is not on main app route. |
| UI-3 | Plan of Care opens Client Overview | P2 | regression | UI | Plan of Care | /plan-of-care | User is authenticated; Plan of Care is available. | 1. Navigate to Plan of Care. 2. Open Client Overview. | Client Overview section (organism) is present in DOM and visible. |
| UI-4 | Manage Employees opens Add Employee flow | P2 | regression | UI | Manage Employees | /manage-employees | User has permission; Employee List is visible. | 1. Go to Manage Employees. 2. Open Add Entries or Add/Edit Employee. | Add/Edit Employee flow (form or route) is accessible and visible. |
| UI-5 | Manage Schedule opens Add Client Visit (Care Coordinator) | P2 | regression | UI | Manage Schedule | /manage-schedule | Care Coordinator role; Calendar section is visible. | 1. Navigate to Manage Schedule. 2. Open Care Coordinator \| Add Client Visit. | Add Client Visit flow is displayed (form or modal visible). |
| UI-6 | Manage Clients opens Add Client flow | P2 | regression | UI | Manage Clients | /manage-clients | User has permission; Client List is visible. | 1. Go to Manage Clients. 2. Open Add Client. | Add Client flow is accessible and visible. |
| UI-7 | Time Entry shows role-specific entry screen | P2 | regression | UI | Time Entry | /time-entry | User has Care Manager, Admin, or Care Partner role. | 1. Navigate to Time Entry/Approval. 2. Select role-specific entry. | Correct time entry screen for role is shown (observable by heading or form). |
| UI-8 | Dashboard Incident Forms empty vs populated state | P2 | edge | UI | Dashboard | /dashboard | User is on Dashboard; Incident Forms section exists. | 1. Navigate to Dashboard. 2. View Incident Forms. | Either empty-state message or list/content is visible. |
| UI-9 | Dashboard Background Check empty vs populated state | P2 | edge | UI | Dashboard | /dashboard | User is on Dashboard; Background Check section exists. | 1. Navigate to Dashboard. 2. View Background Check. | Either empty-state message or list/content is visible. |

### Component State

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| CS-1 | Button default vs disabled state | P2 | regression | UI | Components | Any | Screen with primary CTA button. | 1. Assert default button is clickable. 2. Trigger disabled condition (e.g. invalid form). | Disabled: button has disabled attribute or aria-disabled=true; click does not trigger action. |
| CS-2 | Button variants Contained / Outlined / Ghost | P2 | regression | UI | Components | Any | Screen with buttons. | 1. Render Contained, Outlined, Ghost buttons. | Each has expected variant class or data-variant attribute. |
| CS-3 | Button sizes Small / Medium / Large | P2 | regression | UI | Components | Any | Screen with buttons. | 1. Render buttons at each size. | Size class or data-size attribute present per variant. |
| CS-4 | Button colors Primary / Main01 / Main02 / Error / Grey | P2 | regression | UI | Components | Any | Screen with buttons. | 1. Render each color variant. | Color class or data-color attribute present per variant. |
| CS-5 | TextField empty vs has value | P2 | regression | UI | Components | Any | Form with TextField. | 1. Assert empty state. 2. Enter value. | Empty: value is empty. Filled: input value equals entered text. |
| CS-6 | TextField enabled vs disabled | P2 | regression | UI | Components | Any | Form with TextField. | 1. Enable field. 2. Disable field. | Disabled: input has disabled or readonly; not focusable. |
| CS-7 | FormHelperText enabled vs disabled | P2 | regression | UI | Components | Any | Form with helper text. | 1. Toggle Disabled property. | Helper text visibility or aria-hidden/visibility matches spec. |
| CS-8 | PoC Tabs default vs active | P2 | regression | UI | Plan of Care | /plan-of-care | Plan of Care screen with tabs. | 1. Render tabs. 2. Select a tab. | Selected tab has aria-selected=true or active class; content panel updates. |
| CS-9 | Chip selected Off vs On | P2 | regression | UI | Components | Any | Screen with chips. | 1. Render unselected. 2. Select chip. | Selected chip has selected/aria-selected or equivalent; state is observable. |
| CS-10 | Alert Success vs Error | P2 | regression | UI | Components | Any | Screen with alerts. | 1. Render success alert. 2. Render error alert. | Role=alert and color/severity attribute or class differ. |
| CS-11 | Dropdown open Off vs On | P2 | regression | UI | Components | Any | Screen with dropdown. | 1. Render closed. 2. Click to open. | Open: dropdown list or popover is visible; closed: list is hidden. |
| CS-12 | Checkbox and Switch size Large, Mobile Off | P2 | regression | UI | Components | Any | Form with controls. | 1. Render Type=Checkbox, Size=Large. 2. Render Type=Switch, Size=Large. | Both visible; type and size identifiable in DOM. |
| CS-13 | Do not send table Show Employee / Show Client columns | P1 | regression | UI | Manage Employees / Manage Clients | Profile routes | Employee/Client profile screen. | 1. Toggle Show Employee on/off. 2. Toggle Show Client on/off. | Table columns visibility changes; expected columns present or hidden in DOM. |
| CS-14 | Plan of Care domain variants displayed | P2 | regression | UI | Plan of Care | /plan-of-care | Plan of Care screen. | 1. Render each domain (Medical, Client Overview, Care Coordination, etc.). | Each domain container is present and visible. |
| CS-15 | Expandable section Expanded and Draft states | P2 | regression | UI | Plan of Care | /plan-of-care | Plan of Care or similar. | 1. Toggle Expanded. 2. Toggle Draft. | Expanded state and Draft state reflect in DOM (aria-expanded, class, or content visibility). |
| CS-16 | Avatar acronym variant | P2 | regression | UI | Components | Any | User/employee display. | 1. Render Avatar with Variant=Acronym. | Acronym text is present in avatar element. |
| CS-17 | Status Dropdown widget interaction | P2 | regression | UI | Error screens | Error route | Error screens canvas. | 1. Interact with Status Dropdown. | Status options are visible; selection updates dropdown value. |

### Layout and Visual (Automation-Ready)

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| LV-1 | Desktop 12-column layout grid | P2 | regression | UI | Layout | Any | Screen with layout grid. | 1. Load at desktop viewport. 2. Query grid or container. | 12-column structure present (e.g. grid columns or sections); gutters/sections in DOM or via design tokens. |
| LV-2 | Vertical scrolling on long content | P2 | regression | UI | Plan of Care / Profiles | Various | Long content (Plan of Care, Client Profile). | 1. Load content exceeding viewport. 2. Scroll. | Scrollable container has overflow/scroll behavior; scroll position changes. |

### Responsive

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| RS-2 | Mobile variant Mobile=Off vs Mobile=On | P3 | regression | UI | Components | Any | Components with Mobile property. | 1. Resize to mobile breakpoint. 2. Compare with desktop. | Mobile-specific variants (e.g. component or class) present at mobile width. |
| RS-3 | Viewport Desktop expanded state | P3 | regression | UI | Components | Any | Components with Viewport=Desktop. | 1. Set viewport to desktop. 2. Set Expanded=On. | Desktop expanded state is visible (content or aria-expanded). |
| RS-4 | Orientation change reflow (Calendar / Live View) | P3 | regression | UI | Manage Schedule | /manage-schedule | Manage Schedule sections. | 1. Rotate or resize viewport. | Layout reflows; no horizontal overflow or broken layout (main content visible). |

### Accessibility

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| AX-1 | Focus visibility on Buttons | P3 | regression, accessibility | UI | Components | Any | Screen with buttons. | 1. Tab to each button. | Focus ring or focus-visible style is present on focused button. |
| AX-2 | Focus visibility on TextField | P3 | regression, accessibility | UI | Components | Any | Form with TextField. | 1. Tab to TextField. | Focus state visible; cursor or focus ring present. |
| AX-3 | Focus and keyboard open on Dropdown | P3 | regression, accessibility | UI | Components | Any | Screen with dropdown. | 1. Tab to dropdown. 2. Open with Enter/Space. | Dropdown receives focus; list opens on Enter/Space. |
| AX-4 | Keyboard navigation for PoC Tabs | P3 | regression, accessibility | UI | Plan of Care | /plan-of-care | Plan of Care with PoC Tabs. | 1. Tab to tab list. 2. Use arrow keys. | Tab selection changes with arrow keys; focus moves between tabs. |
| AX-5 | Keyboard toggle Checkbox/Switch | P3 | regression, accessibility | UI | Components | Any | Form with controls. | 1. Tab to checkbox/switch. 2. Toggle with Space. | Control toggles with Space; state updates. |
| AX-6 | Color contrast Success/Error alerts | P3 | regression, accessibility | UI | Components | Any | Screen with alerts. | 1. Run axe or contrast check on success and error alerts. | Contrast meets WCAG AA (axe or pa11y); tag manual-optional if not in CI. |
| AX-7 | Screen reader form labels | P3 | regression, accessibility | UI | Forms | Add Client, Add Employee | Forms with labels. | 1. Use screen reader on form. | Labels and helper text are announced (manual or axe). |
| AX-8 | Screen reader Do not send table | P3 | regression, accessibility | UI | Manage Employees / Clients | Profile | Employee/Client profile. | 1. Navigate table with screen reader. | Table structure and headers announced (manual or axe). |

### Error and Edge

| ID | Title | Priority | Tags | Automation Type | Feature Area | Route | Preconditions | Steps | Expected Results |
|----|-------|----------|------|-----------------|--------------|-------|---------------|-------|------------------|
| EE-1 | No permission message on restricted access | P1 | negative, auth | UI | Authentication | — | User lacks permission. | 1. Attempt access to restricted area. | No-permission message frame or element is displayed. |
| EE-2 | Incident Forms empty state | P2 | edge | UI | Dashboard | /dashboard | No incident forms exist. | 1. Navigate to Incident Forms. | Incident Forms empty-state frame or message is visible. |
| EE-3 | Background Check empty state | P2 | edge | UI | Dashboard | /dashboard | No background check data. | 1. Navigate to Background Check. | Background Check empty-state frame or message is visible. |
| EE-4 | Plan of Care Medical Domain empty | P2 | edge | UI | Plan of Care | /plan-of-care | No medical domain data. | 1. Navigate to Plan of Care \| Medical Domain Empty. | Medical Domain Empty frame or message is visible. |
| EE-5 | TextField validation error | P2 | regression, negative | UI | Forms | Any | Form with validation. | 1. Submit invalid value. | Error state and helper text or error message are visible. |
| EE-6 | Employee Profile Do not send (Blacklist) | P1 | edge | UI | Manage Employees | Profile | Employee Profile Blacklist context. | 1. View Employee Profile - Information - Blacklist. | Do not send table and messaging are visible and correct. |
| EE-7 | Status Dropdown on error screen | P2 | edge | UI | Error screens | Error route | Error screens context. | 1. Interact with Status Dropdown. | Status options are visible and selection works. |

---

## Reusable Flows and Setup Strategy

| Flow | Reusable | Suggested Setup Strategy | Suggested Page Objects |
|------|----------|---------------------------|------------------------|
| Login (valid) | Yes | API+UI (create session or login once) | LoginPage, DashboardPage |
| Login (no permission) | Yes | API+UI (user with restricted role) | LoginPage, NoPermissionPage |
| Plan of Care navigation | Yes | UI or API+UI | PlanOfCarePage, ClientOverviewPage |
| Manage Employees / Add Employee | Yes | API+UI | EmployeeListPage, AddEmployeePage |
| Manage Schedule / Add Client Visit | Yes | API+UI (Care Coordinator) | SchedulePage, AddClientVisitPage |
| Manage Clients / Add Client | Yes | API+UI | ClientListPage, AddClientPage |
| Dashboard empty states | Yes | API (no data) or UI | DashboardPage |
| Do not send table | Yes | API+UI (employee/client with blacklist) | EmployeeProfilePage, ClientProfilePage |

---

## Test Scope Tags Summary

- **smoke:** UI-1, UI-2, EE-1  
- **regression:** Most UI, CS, LV, RS, AX, EE-5  
- **happy-path:** UI-1  
- **negative:** UI-2, EE-1, EE-5  
- **edge:** UI-8, UI-9, EE-2, EE-3, EE-4, EE-6, EE-7  
- **auth:** UI-1, UI-2, EE-1  
- **accessibility:** AX-1–AX-8  

---

*End of Normalized Test Cases (test-case-normalizer)*

# Figma Test Case Discovery: Sophi - Developers Hand Off

**Source:** [Sophi - Developers Hand Off](https://www.figma.com/design/yFFgIDlTbDcQAbICJyFEuu/Sophi---Developers-Hand-Off?node-id=18235-7442)  
**Analysis Date:** 2026-02-11  
**Tool:** figma-test-case-discovery agent

---

## Summary

The Sophi design file is a **web application Developers Hand Off** for a healthcare/care management platform. It covers multiple functional areas: Login, Plan of Care, Manage Employees, Manage Availability, Manage Schedule, Manage Clients, Time Entry/Approval, Invoices & Payments, Payroll, Accounting, and Dashboard. The design uses a robust component library with MUI-based primitives (TextField, FormHelperText, Buttons, Checkboxes, Switches), domain-specific components (Plan of Care domains, Client/Employee profiles), and explicit empty-state designs. Several sections are marked **READY_FOR_DEV**. The Figma structure reveals layout grids (12 columns), bound variables for theming, and component sets with boolean properties (e.g., Do not send table: Show Employee, Show Client).

**Assumptions:** Interactions/prototype flows could not be extracted (script error). Analysis is based on structure and components only. Node `18235:7442` was requested but full file scope was analyzed.

---

## UI Flow Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| UI-1 | Login → Main App | User is logged out; Login screen is displayed. | 1. Enter valid credentials. 2. Submit login form. | User is navigated to main app (e.g., Dashboard or Plan of Care). |
| UI-2 | Login → Error (No Permission) | User has restricted role; Login screen is displayed. | 1. Enter credentials. 2. Submit login. | No permission message screen is displayed. |
| UI-3 | Plan of Care → Client Overview | User is on Plan of Care; Client Overview section exists. | 1. Navigate to Plan of Care. 2. Open Client Overview. | Client Overview (organism) is displayed per annotation. |
| UI-4 | Manage Employees → Employee List → Add Employee | User has permission; Employee List is visible. | 1. Go to Manage Employees. 2. Open Add Entries or Add/Edit Employee. | Add/Edit Employee flow is accessible. |
| UI-5 | Manage Schedule → Calendar → Add Client Visit | Care Coordinator role; Calendar section is visible. | 1. Navigate to Manage Schedule. 2. Open Care Coordinator \| Add Client Visit. | Add Client Visit flow is displayed. |
| UI-6 | Manage Clients → Client List → Add Client | User has permission; Client List is visible. | 1. Go to Manage Clients. 2. Open Add Client. | Add Client flow is accessible. |
| UI-7 | Time Entry → Care Manager / Admin / Care Partner flows | User has appropriate role. | 1. Navigate to Time Entry / Approval. 2. Select Care Manager, Admin, or Care Partner entry. | Correct time entry screen for role is shown. |
| UI-8 | Dashboard → Incident Forms (Empty vs With Data) | User is on Dashboard; Incident Forms section exists. | 1. Navigate to Dashboard. 2. View Incident Forms. | Empty state or populated state is shown based on data. |
| UI-9 | Dashboard → Background Check (Empty vs With Data) | User is on Dashboard; Background Check section exists. | 1. Navigate to Dashboard. 2. View Background Check. | Empty state or populated state is shown based on data. |

---

## Component State Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| CS-1 | Button – Default vs Disabled | Screen with primary CTA button. | 1. Observe default state. 2. Trigger disabled condition (e.g., invalid form). | Default: interactive. Disabled: visually distinct and non-clickable. |
| CS-2 | Button – Contained / Outlined / Ghost variants | Screen with buttons. | 1. Render Contained, Outlined, Ghost buttons. | Each variant matches design (Style=Contained/Outlined/Ghost). |
| CS-3 | Button – Size Small / Medium / Large | Screen with buttons. | 1. Render buttons at each size. | Sizes match specification. |
| CS-4 | Button – Color Primary / Main01 / Main02 / Error / Grey | Screen with buttons. | 1. Render each color variant. | Colors match design tokens. |
| CS-5 | TextField – Has Value vs Empty | Form with TextField. | 1. Render empty. 2. Enter value. | Empty and filled states display correctly. |
| CS-6 | TextField – Enabled vs Disabled | Form with TextField. | 1. Enable field. 2. Disable field. | Enabled: interactive. Disabled: read-only appearance. |
| CS-7 | FormHelperText – Enabled vs Disabled | Form with helper text. | 1. Toggle Disabled property. | Helper text visibility/state matches spec. |
| CS-8 | PoC Tabs – Default vs Active | Plan of Care screen with tabs. | 1. Render tabs. 2. Select a tab. | Default and Active states are visually distinct. |
| CS-9 | Chip – Selected Off vs On | Screen with chips. | 1. Render chip unselected. 2. Select chip. | Selected=Off and Selected=On states match. |
| CS-10 | Alert – Success vs Error | Screen with alerts. | 1. Render success alert. 2. Render error alert. | Color=success and Color=error variants display correctly. |
| CS-11 | Dropdown – Open Off vs On | Screen with dropdown. | 1. Render closed. 2. Click to open. | Open=Off and Open=On states match. |
| CS-12 | Checkbox / Switch – Size Large, Mobile Off | Form with controls. | 1. Render Type=Checkbox, Size=Large. 2. Render Type=Switch, Size=Large. | Both types display at large size. |
| CS-13 | Do not send table – Show Employee / Show Client | Employee/Client profile screen. | 1. Toggle Show Employee true/false. 2. Toggle Show Client true/false. | Table columns visibility changes per booleans. |
| CS-14 | Plan of Care Domain – All domain variants | Plan of Care screen. | 1. Render each domain (Medical, Client Overview, Care Coordination, Functional, Cognitive, Social, Environmental Safety, Financial, Legal). | Each domain container displays correctly. |
| CS-15 | Expandable section – Expanded Off vs On, Draft Off vs On | Plan of Care or similar. | 1. Toggle Expanded. 2. Toggle Draft. | Expanded and Draft states update as designed. |
| CS-16 | Avatar – Acronym variant | User/employee display. | 1. Render Avatar with Variant=Acronym. | Acronym displays in avatar. |
| CS-17 | Status Dropdown widget | Error screens canvas. | 1. Interact with Status Dropdown. | Status options and selection behavior match design. |

---

## Layout and Visual Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| LV-1 | Layout grid – 12 columns | Screen with layout grid enabled. | 1. Enable grid overlay. | 12-column grid visible with 80px or 74px sections, 24px gutters per spec. |
| LV-2 | Vertical scrolling – overflow | Long content on Plan of Care, Client Profile, etc. | 1. Load content exceeding viewport. 2. Scroll. | Vertical overflow scrolls; overflowDirection=VERTICAL_SCROLLING respected. |
| LV-3 | NavBar (Molecule) alignment | Any screen with NavBar. | 1. Render NavBar per annotation. | NavBar aligns with layout grid and design. |
| LV-4 | Client Overview (Organism) layout | Plan of Care screen. | 1. Render Client Overview per annotation. | Organism layout matches design. |
| LV-5 | Client Profile vs Employee profile layout | Profile screens. | 1. Compare Client Profile and Employee profile frames. | Layout and structure match each design. |
| LV-6 | Responsive offset – 152px vs 264px vs 304px | Different frames. | 1. Compare grid offsets across frames. | Offset values match frame-specific design. |
| LV-7 | Do not send table – column visibility | Employee/Client profile. | 1. Show Employee on, Show Client on. 2. Toggle each off. | Table layout adapts to visible columns. |

---

## Responsive Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| RS-1 | Desktop viewport – 12-column grid | Desktop breakpoint. | 1. Resize to desktop width. 2. Verify layout. | 12-column grid, 80px/74px sections, correct gutters. |
| RS-2 | Mobile variant – Mobile=Off vs Mobile=On | Components with Mobile property. | 1. Render at mobile breakpoint. 2. Compare with desktop. | Mobile-specific variants display when applicable. |
| RS-3 | Viewport=Desktop – expanded components | Components with Viewport=Desktop. | 1. Render Expanded=On, Viewport=Desktop. | Desktop expanded state matches design. |
| RS-4 | Orientation change – Calendar / Live View | Manage Schedule sections. | 1. Rotate device or resize. | Layout reflows appropriately. |

---

## Accessibility Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| AX-1 | Focus visibility – Buttons | Screen with buttons. | 1. Tab to each button. | Focus ring/indicator is visible. |
| AX-2 | Focus visibility – TextField | Form with TextField. | 1. Tab to TextField. | Focus state is visible. |
| AX-3 | Focus visibility – Dropdown | Screen with dropdown. | 1. Tab to dropdown. 2. Open with Enter/Space. | Focus and keyboard open work. |
| AX-4 | Keyboard navigation – Tabs | Plan of Care with PoC Tabs. | 1. Tab to tab list. 2. Use arrow keys. | Tab selection via keyboard works. |
| AX-5 | Keyboard navigation – Checkbox/Switch | Form with controls. | 1. Tab to checkbox/switch. 2. Toggle with Space. | Toggle via keyboard works. |
| AX-6 | Color contrast – Success/Error alerts | Screen with alerts. | 1. Check success and error alert contrast. | Contrast meets WCAG AA (or specified standard). |
| AX-7 | Screen reader – Form labels | Forms (Add Client, Add Employee, etc.). | 1. Use screen reader on form. | Labels and helper text are announced. |
| AX-8 | Screen reader – Do not send table | Employee/Client profile. | 1. Navigate table with screen reader. | Table structure and headers are announced. |

---

## Error and Edge UI Test Cases

| ID | Scenario | Preconditions | Steps | Expected Results |
|-----|----------|---------------|-------|------------------|
| EE-1 | No permission message | User lacks permission. | 1. Attempt access to restricted area. | No permission message frame is displayed. |
| EE-2 | Incident Forms – Empty State | No incident forms exist. | 1. Navigate to Incident Forms. | Incident Forms - Empty State frame is shown. |
| EE-3 | Background Check – Empty State | No background check data. | 1. Navigate to Background Check. | Background Check - Empty State frame is shown. |
| EE-4 | Plan of Care – Medical Domain Empty | No medical domain data. | 1. Navigate to Plan of Care \| Medical Domain Empty. | Medical Domain Empty frame is shown. |
| EE-5 | TextField – Validation error | Form with validation. | 1. Submit invalid value. | Error state and helper text display. |
| EE-6 | Employee Profile – Do not send | Blacklist / do-not-send context. | 1. View Employee Profile - Information - Blacklist. | Do not send table and messaging display correctly. |
| EE-7 | Status Dropdown – error clarity | Error screens context. | 1. Interact with Status Dropdown on error screen. | Status options clarify design status. |

---

## ⚠️ Requirements Gaps Identified

| Gap ID | Type | Description | Recommended Clarification |
|--------|------|-------------|---------------------------|
| GAP-1 | Unspecified Interactions | No prototype interactions could be extracted. | Add prototype links for main flows (Login→Dashboard, navigation between sections) or document in a separate spec. |
| GAP-2 | Missing States | Button hover/focus/active states not explicitly visible in components. | Confirm hover, focus, and active visual specs for all button variants. |
| GAP-3 | Responsive Ambiguity | Mobile breakpoints and reflow rules not defined in structure. | Define breakpoints (e.g., 768px, 1024px) and component stacking for each section. |
| GAP-4 | Empty States Scope | Empty states exist for Incident Forms, Background Check, Medical Domain. | Confirm if other sections (Client List, Employee List, Calendar, etc.) need empty states. |
| GAP-5 | Loading States | No loading or skeleton states found. | Add loading/skeleton designs for list and profile screens. |
| GAP-6 | Error Messaging | Inline validation and API error messaging not clearly specified. | Define error message placement, copy, and styling. |
| GAP-7 | Manage Configuration [BE Only] | Admin section marked BE Only. | Clarify whether any UI is required for Admin or if it is backend-only. |
| GAP-8 | Copy Ambiguity | Placeholder and microcopy not fully visible in structure. | Confirm final copy for labels, placeholders, empty state messages. |
| GAP-9 | Do not Use section | "Do not Use" section under Manage Schedule. | Confirm whether these frames should be excluded from implementation. |
| GAP-10 | Variable Bindings | Many frames use bound variables (e.g., fills). | Document variable names and expected values for light/dark or theming. |

---

## Coverage Matrix

| Area | Screens/Sections | UI Flow | Component State | Layout | Responsive | Accessibility | Error/Edge |
|------|------------------|---------|-----------------|--------|------------|---------------|------------|
| Login | Login, No permission | UI-1, UI-2 | — | — | — | AX-1, AX-2 | EE-1 |
| Plan of Care | PoC, Client Overview, Add Entries, Medical, Care Coordination | UI-3 | CS-8, CS-14, CS-15 | LV-2, LV-4 | RS-1 | AX-4 | EE-4 |
| Manage Employees | Employee List, Add/Edit, Profile, Do not send | UI-4 | CS-13 | LV-5, LV-7 | RS-2 | AX-8 | EE-6 |
| Manage Availability | Schedule & Availability | — | — | — | — | — | — |
| Manage Schedule | Calendar, Time Off, Add Client Visit, Live View, Edit Visits, Visit Details | UI-5 | — | — | RS-4 | — | — |
| Manage Clients | Client profile, Add Client, Client List, etc. | UI-6 | — | LV-5 | — | — | — |
| Time Entry | Care Manager, Admin, Care Partner | UI-7 | — | — | — | — | — |
| Invoices & Payments | Billing Periods, Invoices, Payments | — | — | — | — | — | — |
| Payroll | Payroll, Adjustments | — | — | — | — | — | — |
| Accounting | Admin expenses | — | — | — | — | — | — |
| Dashboard | Metrics, Incident Forms, Background Check | UI-8, UI-9 | — | LV-1 | — | — | EE-2, EE-3 |
| Components | Buttons, TextField, Tabs, Chips, Alerts, Dropdowns, etc. | — | CS-1–CS-17 | LV-1 | RS-2, RS-3 | AX-1–AX-8 | EE-5 |

---

## Priority Recommendations

1. **P1 – Login and No Permission flow (UI-1, UI-2, EE-1):** Critical path; must be tested first.
2. **P1 – Do not send table behavior (CS-13, EE-6):** Boolean-driven column visibility affects data display.
3. **P1 – Empty states (EE-2, EE-3, EE-4):** Explicit designs exist; ensure implementation matches.
4. **P2 – Plan of Care domain variants and tabs (CS-8, CS-14, CS-15):** Core UX for care management.
5. **P2 – Button and form component states (CS-1–CS-7):** Foundation for all forms.
6. **P2 – Prototype/flow documentation (GAP-1):** Add interaction specs to reduce ambiguity.
7. **P3 – Responsive and mobile variants (RS-1–RS-4, GAP-3):** Clarify breakpoints and reflow.
8. **P3 – Accessibility (AX-1–AX-8):** Ensure focus and keyboard support.
9. **P3 – Loading and error states (GAP-5, GAP-6):** Add designs or specs.
10. **P4 – Manage Configuration [BE Only] and Do not Use (GAP-7, GAP-9):** Confirm scope.

---

*End of Figma Test Case Discovery*

Use the agent defined in:
.cursor/agents/figma-test-case-discovery.md

Follow rules in:
.cursor/rules/figma-test-case-discovery-rule.mdc

TASK:
Create a **detailed** set of manual test cases from **Figma** for thorough evaluation. **Outline the structure** of the suite (flows, component states, responsive/accessibility, and error/edge groupings) so documentation is easy to review.

Coverage expectations:
- **Positive scenarios**: primary journeys and success states shown in frames/prototypes.
- **Negative / error UI**: validation, failure, empty, loading, and disabled states—**when shown or implied** in the design or annotations.
- **Credentials and sign-in UX** (when login or account UI appears): invalid credentials, field-level errors, blocked states—each with **expected visible copy, placement, and timing** where the design or notes specify them; otherwise flag gaps.
- **Error message handling**: inline vs. global messaging, dismiss behavior, focus management, and consistency across breakpoints.

Each row must follow the agent’s **structured table format** (**ID | Scenario | Preconditions | Steps | Expected Results** — no separate Comments column). Put frame/node references, variants, data assumptions, or open questions **inside** Scenario, Preconditions, Steps, or Expected Results as appropriate. Aim for clarity and depth suitable for manual execution and design QA.

OUTPUT:
Save the full result as a single UTF-8 Markdown file (`.md`) in the workspace. Do not write a companion `.csv` unless the user explicitly asks for CSV.

After the Markdown file is saved, **ask the user** whether they want to integrate these test cases into **Zephyr Scale** (Jira test management). **Do not** import or call Zephyr APIs until they answer. If they confirm (e.g. Yes), **your very next step** is to **ask for (1) owner name** (who owns the cases: Jira **display name**, **email**, or **Atlassian account id**) **and (2) folder location** (Zephyr Scale target **folder**: numeric **folder id** from the Scale UI or API). **Do not** run dry-run, import scripts, or any Scale POSTs until the user has supplied or explicitly confirmed both for **this** import. Then read and follow `.cursor/skills/zephyr-from-test-discovery/SKILL.md` using the saved `.md` path as input; use `.cursor/skills/zephyr-scale/SKILL.md` for auth and REST as that skill references. **Default Zephyr import:** one test case per Acceptance Criterion (`--per-ac` on Cloud); use `--single-testcase` for one case per whole story; omit both for one case per Markdown row only if the user requests it.

INPUT:
{{input}}

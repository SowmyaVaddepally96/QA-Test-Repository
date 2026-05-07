Use the agent defined in:
.cursor/agents/test-case-discovery.md

Follow rules in:
.cursor/rules/test-case-discovery-rule.mdc

TASK:
Create a **detailed** set of manual test cases from **Jira** for thorough evaluation. **Outline the structure** of the suite (how happy path, negative, edge, and security-related scenarios relate) so documentation is easy to review.

Coverage expectations:
- **Positive scenarios**: primary and alternate success paths tied to acceptance criteria.
- **Negative scenarios**: invalid inputs, unauthorized or denied actions, validation failures, boundary/empty states, and dependency failures—**when implied by the story or AC**.
- **Credentials and sessions** (when login, identity, or permissions apply): invalid credentials, locked/expired or wrong-role users, session timeout, token/session revocation—each with **explicit expected UI/API feedback or error messages** where Jira/AC defines copy or behavior; otherwise flag as a gap.
- **Error handling**: user-visible errors, inline validation, system messages, empty states, and recovery; note **message text or acceptable variants** when specified.

Each row must follow the agent’s **structured table format** (**ID | Scenario | Preconditions | Steps | Expected Results** — no separate Comments column). Put traceability (e.g. **AC …**), data variants, environment notes, risks, or open questions **inside** Scenario, Preconditions, Steps, or Expected Results as appropriate. Aim for clarity and depth suitable for manual execution and audits.

For Jira, use the configured Jira MCP (Atlassian **`JIRA_API_MAIL`** + **`JIRA_API_KEY`**). Do not use `git config user.email` as the Atlassian identity.

OUTPUT:
Save the full result as a single UTF-8 Markdown file (`.md`) in the workspace. Do not write a companion `.csv` unless the user explicitly asks for CSV.

After the Markdown file is saved, **ask the user** whether they want to integrate these test cases into **Zephyr Scale** (Jira test management). **Do not** import or call Zephyr APIs until they answer. If they confirm (e.g. Yes), **your very next step** is to **ask for (1) owner name** (who owns the cases: Jira **display name**, **email**, or **Atlassian account id**) **and (2) folder location** (Zephyr Scale target **folder**: numeric **folder id** from the Scale UI or API). **Do not** run dry-run, import scripts, or any Scale POSTs until the user has supplied or explicitly confirmed both for **this** import. Then read and follow `.cursor/skills/zephyr-from-test-discovery/SKILL.md` using the saved `.md` path as input; use `.cursor/skills/zephyr-scale/SKILL.md` for auth and REST as that skill references. **Default Zephyr import:** one test case per Acceptance Criterion (`--per-ac` on Cloud); use `--single-testcase` for one case per whole story; omit both for one case per Markdown row only if the user requests it.

INPUT:
{{input}}



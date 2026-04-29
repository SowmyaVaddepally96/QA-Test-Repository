Use the agent defined in:
.cursor/agents/figma-test-case-discovery.md

Follow rules in:
.cursor/rules/figma-test-case-discovery-rule.mdc

TASK:
Write manual test cases from figma

OUTPUT:
Save the full result as a single UTF-8 Markdown file (`.md`) in the workspace. Do not write a companion `.csv` unless the user explicitly asks for CSV.

After the Markdown file is saved, **ask the user** whether they want to integrate these test cases into **Zephyr Scale** (Jira test management). **Do not** import or call Zephyr APIs until they answer. If they confirm (e.g. Yes), **your very next step** is to **ask for (1) owner name** (who owns the cases: Jira **display name**, **email**, or **Atlassian account id**) **and (2) folder location** (Zephyr Scale target **folder**: numeric **folder id** from the Scale UI or API). **Do not** run dry-run, import scripts, or any Scale POSTs until the user has supplied or explicitly confirmed both for **this** import. Then read and follow `.cursor/skills/zephyr-from-test-discovery/SKILL.md` using the saved `.md` path as input; use `.cursor/skills/zephyr-scale/SKILL.md` for auth and REST as that skill references. **Default Zephyr import:** one test case per Jira user story (`--single-testcase` on Cloud) unless the user requests one case per scenario row.

INPUT:
{{input}}

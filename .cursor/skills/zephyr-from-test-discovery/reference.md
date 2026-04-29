# Zephyr from test-discovery — reference

## Official API docs

- Zephyr Scale **Cloud** v2: https://support.smartbear.com/zephyr-scale-cloud/api-docs/  
- Zephyr Scale **Server/DC** v1: https://support.smartbear.com/zephyr-scale-server/api-docs/v1/

## Endpoints used (Cloud)

| Step | Method | Path (after `{ZEPHYR_CLOUD_BASE_URL}`) |
|------|--------|----------------------------------------|
| Create test case | POST | `/testcases` |
| Step-by-step script | POST | `/testcases/{testCaseKey}/teststeps` — body `{"mode":"OVERWRITE","items":[{"inline":{"description":"...","testData":"...","expectedResult":"..."}}]}` |
| Traceability (story link) | POST | `/testcases/{testCaseKey}/links/issues` — body `{"issueId": <numeric>}` |

Resolve Jira **numeric id** and **Summary** (issue title) from key (Jira Cloud):

- `GET {JIRA_CLOUD_URL}/rest/api/3/issue/{KEY}` with Basic auth `email:api_token` → JSON fields `id` and `fields.summary`. The Summary is used as the Zephyr test case **name** for **`--single-testcase`** imports (when present); otherwise the Markdown metadata table row **Summary** is used, then a fallback name including the story key.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `ZEPHYR_PROJECT_KEY` | Scale project key (e.g. `HBGDIGI`) |
| `ZEPHYR_ACCESS_TOKEN` | Scale Cloud Bearer token (create in Jira → Zephyr Scale → API access tokens; validate with `zephyr_request.py ping` or import preflight before live POST) |
| `ZEPHYR_CLOUD_BASE_URL` | Default `https://api.zephyrscale.smartbear.com/v2` (EU: `https://eu.api.zephyrscale.smartbear.com/v2`) |
| `ZEPHYR_JIRA_KEY` | Story key for naming / resolve |
| `ZEPHYR_OWNER_ID` | Atlassian account id for Zephyr **Owner** |
| `ZEPHYR_FOLDER_ID` | Numeric folder id — all cases in one import go here |
| `ZEPHYR_JIRA_ISSUE_ID` | Numeric Jira issue id if not using Jira REST resolve |
| `JIRA_CLOUD_URL` | Jira site base URL (e.g. `https://hornblower.atlassian.net`) |
| `JIRA_API_MAIL` / `JIRA_API_EMAIL` | Atlassian account email for Jira REST |
| `JIRA_API_KEY` / `JIRA_API_TOKEN` | Atlassian API token |
| `ZEPHYR_STATUS_NAME` | Override default **Approved**; empty string omits `statusName` |
| `ZEPHYR_COMPONENT_ID` | Optional Scale **component** numeric id |
| `ZEPHYR_SKIP_ISSUE_LINK` | `1` to skip `links/issues` (emergency only) |
| `ZEPHYR_CUSTOM_FIELDS_JSON` | Extra Scale custom fields (see zephyr-scale skill) |

## Section detection rules

### Requirements / code discovery (`test-case-discovery`)

- **Import** `## Happy Path Test Cases` and `## Negative Test Cases` tables only.  
- **Do not import** Edge, Security, Automation Assessment, gaps-only tables.

### Figma discovery (`figma-test-case-discovery`)

- **Import** `## UI Flow Test Cases` and `## Error and Edge UI Test Cases` only.

### Auto-detect format

If the file contains `## UI Flow Test Cases`, use **figma** section rules; else **discovery**.

## Idempotency

Re-running the script **creates duplicate** test cases unless you delete them in Zephyr first.

With **`--single-testcase`**, each run still **POSTs a new** test case (Scale has no “upsert by name” in this script). To replace a consolidated case, delete the old one in Zephyr, then re-import.

## Troubleshooting

| Symptom | Check |
|--------|--------|
| 400 on create | Required Scale custom fields — use `ZEPHYR_CUSTOM_FIELDS_JSON` (see zephyr-scale SKILL). |
| 400 on teststeps | Payload shape / max steps; confirm Cloud vs Server. |
| 403 on issue link | Token scopes; issue in same Jira as Scale. |
| Wrong component in UI | `ZEPHYR_COMPONENT_ID` or project-specific custom field names. |

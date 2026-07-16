---
name: zephyr-scale
description: >-
  Interacts with Zephyr Scale (SmartBear test management for Jira) over REST for
  private Jira Server/Data Center and Jira Cloud. Covers base URLs, Bearer tokens
  (Cloud), Basic auth with Jira credentials or PAT (Server/DC), environment setup,
  and curl/Python examples. Use when the user mentions Zephyr Scale, TM4J, /rest/atm/,
  test cases/cycles/plans in Jira, or syncing tests with a private or on‑prem Jira.
---

# Zephyr Scale (private / on‑prem / Cloud)

## What this skill covers

**Zephyr Scale** is SmartBear’s Jira‑integrated test management product. A **private** instance usually means **Jira Server or Jira Data Center** on your network (VPN). **Jira Cloud** with Zephyr Scale is still “private” to your org, but the Scale REST API is hosted by SmartBear at a public base URL with a **Bearer** token.

Do **not** confuse with **Zephyr Squad** (different product and API paths).

## Choose your deployment

| Deployment | API base | Typical auth |
|------------|----------|----------------|
| **Jira Cloud + Zephyr Scale** | `https://api.zephyrscale.smartbear.com/v2` (EU: `https://eu.api.zephyrscale.smartbear.com/v2`) | `Authorization: Bearer <access_token>` |
| **Jira Server / Data Center + Zephyr Scale** | `{JIRA_BASE_URL}/rest/atm/1.0` (paths continue under `/rest/atm/1.0/...`) | HTTP **Basic** `base64(user:password)` — password can be a Jira **PAT** on supported versions |

**Private network:** For Server/DC, the machine running curl/scripts (or the agent’s environment) must reach `JIRA_BASE_URL` (VPN, split tunnel, etc.). There is no separate “public Scale URL” for on‑prem; everything goes to your Jira host.

## Credentials and `.env` (recommended)

Put a `.env` next to this skill (e.g. `.cursor/skills/zephyr-scale/.env`) or in the repo root. **Do not commit secrets.**

### Jira Cloud + Zephyr Scale

1. In Jira: **Zephyr Scale → Settings** (or profile menu, depending on version) and create an **API access token / Bearer token** (wording varies; see SmartBear Cloud docs).
2. Set:

```bash
ZEPHYR_DEPLOYMENT=cloud
ZEPHYR_CLOUD_BASE_URL=https://api.zephyrscale.smartbear.com/v2
# If your org is on EU infrastructure:
# ZEPHYR_CLOUD_BASE_URL=https://eu.api.zephyrscale.smartbear.com/v2
ZEPHYR_ACCESS_TOKEN=eyJ...
ZEPHYR_PROJECT_KEY=PROJ
```

### Jira Server / Data Center + Zephyr Scale

1. Use a Jira user that has Zephyr Scale permissions in the target projects.
2. Prefer **PAT as password** where Jira supports it (`user` = Jira username, `password` = PAT).
3. Set:

```bash
ZEPHYR_DEPLOYMENT=server
ZEPHYR_JIRA_BASE_URL=https://jira.yourcompany.internal
ZEPHYR_JIRA_USER=automation.user
ZEPHYR_JIRA_PASSWORD=secret_or_pat
ZEPHYR_PROJECT_KEY=PROJ
```

Environment variables already set in the shell override `.env`.

## Access token before **adding** or updating test cases (Cloud)

Zephyr Scale Cloud does **not** publish a token-issuing REST endpoint you can call with client id/secret like some OAuth APIs. The **Bearer** value is an **API access token** (JWT) that each user creates in **Jira** (Zephyr Scale → API access tokens / Zephyr API keys — wording varies by version). Treat **obtaining** the token as: **load `ZEPHYR_ACCESS_TOKEN` from `.env`/secrets**, and **confirm it still works** right before any write.

**Whenever you create or update test cases** (POST/PATCH to Scale Cloud):

1. Ensure `ZEPHYR_ACCESS_TOKEN` (or `ZEPHYR_SCALE_TOKEN`) is set; if missing, **do not POST**. Tell the user to create a token in Jira, paste it into `.env` (never into chat), and save.
2. **Validate immediately before writes:** from repo root run  
   `python .cursor/skills/zephyr-scale/scripts/zephyr_request.py ping`  
   Exit code **0** means the token and `ZEPHYR_PROJECT_KEY` are accepted. **401** means the token is missing, revoked, or wrong — have the user **generate a new token** in Jira, update `.env`, and ping again.
3. The **import** script (zephyr-from-test-discovery) runs the same check automatically on **live** Cloud imports (not `--dry-run`).

**Server/DC:** writes use Basic auth (`ZEPHYR_JIRA_USER` + password/PAT); there is no separate Scale Bearer. Still verify connectivity with `ping` before bulk creates.

## Quick verification (curl)

**Cloud** — list a few test cases (adjust query params per [Cloud API docs](https://support.smartbear.com/zephyr-scale-cloud/api-docs/)):

```bash
curl -sS -H "Authorization: Bearer $ZEPHYR_ACCESS_TOKEN" \
  "$ZEPHYR_CLOUD_BASE_URL/testcases?projectKey=$ZEPHYR_PROJECT_KEY&maxResults=5"
```

**Server/DC** — example authenticated call to the Scale REST prefix (exact resource path depends on version; see Server v1 docs):

```bash
AUTH=$(printf '%s:%s' "$ZEPHYR_JIRA_USER" "$ZEPHYR_JIRA_PASSWORD" | base64)
curl -sS -H "Authorization: Basic $AUTH" -H "Accept: application/json" \
  "$ZEPHYR_JIRA_BASE_URL/rest/atm/1.0/testcase?projectKey=$ZEPHYR_PROJECT_KEY"
```

If you get **401/403**, fix user permissions, PAT scope, or VPN connectivity. If you get **404** on `/rest/atm/1.0/...`, confirm the Zephyr Scale app is installed and the path matches your version (see [reference.md](reference.md)).

## Helper script (optional)

From repo root, after configuring `.env`:

```bash
python .cursor/skills/zephyr-scale/scripts/zephyr_request.py ping
```

Uses `ZEPHYR_DEPLOYMENT` and the variables above to send a minimal authenticated **GET** (Cloud: `/v2/testcases`; Server: `/rest/atm/1.0/testcase`) with `projectKey`. Uses Python **stdlib only** (no `pip install`). If Server returns **404** or **405**, your version may use a different list endpoint—check the Server v1 API docs linked in [reference.md](reference.md).

## Agent workflow

1. **Identify deployment** from user (Cloud vs Server/DC) or URLs (`api.zephyrscale.smartbear.com` → Cloud; company Jira host → Server/DC).
2. **Never ask for passwords or API tokens in chat**; use `.env` or CI secrets.
3. **Before any Scale write (especially creating test cases):** for Cloud, **ensure a valid Bearer** — run `zephyr_request.py ping` (or rely on the import script’s preflight). On **401**, stop and have the user **create a new Zephyr Scale API access token in Jira** and update `ZEPHYR_ACCESS_TOKEN`; there is no separate programmatic “get token” HTTP call for Scale Cloud.
4. For **read** operations (list test cases, cycles, links), prefer GET with tight `maxResults` while exploring.
5. For **write** operations (create test case, execution, attachments), confirm project key, required JSON body, and idempotency expectations with the user before calling POST/PUT. **Whenever you start creating test cases** (not only via the discovery import script), **ask the user for the Zephyr folder id** (numeric) and **who will own the cases** (**Jira display name**, **email**, or **Atlassian account id**) first—or have them explicitly confirm reusing folder and owner from this chat / `.env` for **this** run. Do not assume `.env` alone is consent for this session; resolve name/email to **account id** when the API requires it and confirm before POST.
6. Point the user to **official** SmartBear docs for full schemas; use [reference.md](reference.md) for links and product disambiguation.

## Additional resources

- Links, paths, and “Scale vs Squad” notes: [reference.md](reference.md)
- Import **test-case-discovery** / **figma-test-case-discovery** Markdown into Scale (happy path + negative only; **default: one Zephyr test case per Acceptance Criterion** via `--per-ac`): [../zephyr-from-test-discovery/SKILL.md](../zephyr-from-test-discovery/SKILL.md)
- **Clone Test Cycles folder tree** (subfolders + cycles + assignments; source folder name + new folder name): [../zephyr-clone-test-cycle-folder/SKILL.md](../zephyr-clone-test-cycle-folder/SKILL.md)

# Zephyr Scale — reference links and notes

## Official documentation

- **Zephyr Scale for Jira Cloud API:** https://support.smartbear.com/zephyr-scale-cloud/api-docs/  
  - Base URL (typical): `https://api.zephyrscale.smartbear.com/v2`  
  - EU (typical): `https://eu.api.zephyrscale.smartbear.com/v2`  
  - Auth: `Authorization: Bearer <token>`

- **Zephyr Scale Server / Data Center API (v1):** https://support.smartbear.com/zephyr-scale-server/api-docs/v1/  
  - Base URL pattern: `{JIRA_BASE_URL}/rest/atm/1.0`  
  - SmartBear’s Server examples often use **HTTP Basic** with Jira username and password (or PAT as password): https://github.com/SmartBear/zephyr-scale-api-v1-examples  

- **Server REST automation scripts (Node):** https://github.com/SmartBear/zephyr-scale-server-rest-api-scripts  

## Product disambiguation

| Name | API hint |
|------|-----------|
| **Zephyr Scale** (TM4J) | Cloud: `api.zephyrscale.smartbear.com/v2`. Server/DC: `/rest/atm/1.0/...` |
| **Zephyr Squad** (older “Zephyr for Jira”) | Different base URLs and headers (e.g. `zapiAccessKey`, JWT for Cloud; `/rest/zapi/latest/` on Server). Not covered by this skill. |

## Private / on‑prem checklist

- [ ] Confirm product is **Zephyr Scale**, not Squad.  
- [ ] Confirm Jira base URL is reachable from where scripts run (VPN, DNS, TLS).  
- [ ] Server/DC: Jira user (or PAT) has Scale permissions in the project.  
- [ ] Cloud: token created from Zephyr Scale in Jira; correct regional base URL if applicable. Before creates, run `scripts/zephyr_request.py ping` (import script preflights Bearer on live Cloud import).  

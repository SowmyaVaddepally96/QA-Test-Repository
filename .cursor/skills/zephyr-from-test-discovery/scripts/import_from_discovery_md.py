#!/usr/bin/env python3
"""
Parse test-case-discovery / figma-test-case-discovery Markdown and create
Zephyr Scale test cases (happy path + negative sections only).

Cloud workflows:
  - Per AC (--per-ac, recommended): One Zephyr test case **per Acceptance Criterion**. Group rows using
    **AC …** tags in Scenario, Preconditions, or optional legacy Comments. Name = `{Jira Summary} — AC …`.
    Same traceability link on each case.
  - Consolidated (--single-testcase): One Zephyr **name** = whole story (Jira **Summary**); all rows
    as steps in one case.

Loads .env like zephyr-scale/scripts/zephyr_request.py (stdlib only).

Usage:
  python import_from_discovery_md.py test-cases-PROJ-123.md [--dry-run] [--strict]
  python import_from_discovery_md.py test.md --jira-key PROJ-123 --owner-id ... --folder-id ...
  python import_from_discovery_md.py test.md --per-ac --owner-id ... --folder-id ...
      # one Scale test case per AC (AC tags in Scenario/Preconditions/Comments); Test Script = one step per row in that AC
  python import_from_discovery_md.py test.md --single-testcase --owner-id ... --folder-id ...
      # one Scale test case for whole story; Test Script = one step per HP/NEG row
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Literal

Policy = Literal["skip", "hp", "neg"]


def load_dotenv() -> None:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / ".env",
        Path.cwd() / ".env",
    ]
    extra = os.environ.get("ZEPHYR_ENV_FILE")
    if extra:
        candidates.insert(0, Path(extra))
    for p in candidates:
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
        break


def extract_jira_key(markdown_text: str, filename: str | None) -> str | None:
    """Resolve PROJ-123 from filename test-cases-PROJ-123.md or first **Jira:** line."""
    if filename:
        m = re.search(r"([A-Z][A-Z0-9]+-\d+)", Path(filename).stem, re.I)
        if m:
            return m.group(1).upper()
    for line in markdown_text.splitlines()[:40]:
        if "jira" in line.lower() and "browse" in line.lower():
            m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)", line, re.I)
            if m:
                return m.group(1).upper()
        m = re.match(r"^\*\*Jira:\*\*\s*\[([A-Z][A-Z0-9]+-\d+)", line, re.I)
        if m:
            return m.group(1).upper()
    return None


def extract_summary_section(markdown_text: str) -> str:
    """First ## Summary block (plain text) for Zephyr Description."""
    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        if re.match(r"^##\s+Summary\s*$", lines[i], re.I):
            buf: list[str] = []
            i += 1
            while i < len(lines) and not re.match(r"^##\s+", lines[i]):
                buf.append(lines[i])
                i += 1
            return re.sub(r"\s+", " ", "\n".join(buf).strip())[:12000]
        i += 1
    return ""


def infer_component_label(markdown_text: str) -> str | None:
    """
    Map ticket hints: FE -> Frontend, BE -> Backend (from title/summary lines).
    If both appear, prefer Frontend when FE present; else Backend.
    """
    head = "\n".join(markdown_text.splitlines()[:25])
    has_fe = bool(re.search(r"\bFE\b", head))
    has_be = bool(re.search(r"\bBE\b", head))
    if has_fe:
        return "Frontend"
    if has_be:
        return "Backend"
    return None


def split_step_items(steps: str, test_data: str, expected: str) -> list[dict[str, str]]:
    """Build Zephyr Scale inline test steps (step-by-step script)."""
    steps = (steps or "").strip()
    test_data = (test_data or "").strip()
    expected = (expected or "").strip()
    parts = [s.strip() for s in re.split(r"\s*;\s*", steps) if s.strip()]
    if len(parts) <= 1:
        return [
            {
                "description": steps or "(no steps)",
                "testData": test_data,
                "expectedResult": expected,
            }
        ]
    items: list[dict[str, str]] = []
    for idx, p in enumerate(parts):
        items.append(
            {
                "description": p,
                "testData": test_data if idx == 0 else "",
                "expectedResult": expected if idx == len(parts) - 1 else "",
            }
        )
    return items


def jira_get_issue_id_and_summary(
    cloud_base: str, email: str, api_token: str, issue_key: str
) -> tuple[str | None, str | None]:
    """GET Jira Cloud issue: numeric id for Scale traceability + fields.summary for Zephyr name."""
    cloud_base = cloud_base.rstrip("/")
    auth = base64.b64encode(f"{email}:{api_token}".encode("utf-8")).decode("ascii")
    url = f"{cloud_base}/rest/api/3/issue/{urllib.parse.quote(issue_key)}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Basic {auth}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            iid = data.get("id")
            id_str = str(iid) if iid is not None else None
            fields = data.get("fields") or {}
            summ = fields.get("summary")
            summary_str = summ.strip() if isinstance(summ, str) else None
            return id_str, summary_str
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"Jira GET {issue_key} failed HTTP {e.code}: {err[:1500]}", file=sys.stderr)
        return None, None
    except urllib.error.URLError as e:
        print(f"Jira GET failed: {e}", file=sys.stderr)
        return None, None


def resolve_jira_issue_for_import(jira_key: str | None, explicit_id: str | None) -> tuple[str | None, str | None]:
    """
    Returns (numeric_issue_id, issue_summary from Jira).
    When ZEPHYR_JIRA_ISSUE_ID is set, still loads summary from Jira REST if jira_key + Cloud creds exist.
    """
    site = (os.environ.get("JIRA_CLOUD_URL") or os.environ.get("ATLASSIAN_SITE_URL") or "").strip().rstrip("/")
    email = (os.environ.get("JIRA_API_EMAIL") or os.environ.get("JIRA_API_MAIL") or "").strip()
    token = (os.environ.get("JIRA_API_TOKEN") or os.environ.get("JIRA_API_KEY") or "").strip()

    fetched_id: str | None = None
    fetched_summary: str | None = None
    if jira_key and site and email and token:
        fetched_id, fetched_summary = jira_get_issue_id_and_summary(site, email, token, jira_key)

    if explicit_id and explicit_id.strip():
        return explicit_id.strip(), fetched_summary

    if not jira_key:
        return None, None
    if fetched_id is not None or fetched_summary is not None:
        return fetched_id, fetched_summary
    return None, None


def strip_md(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^\*+", "", s)
    s = re.sub(r"\*+$", "", s)
    return s.strip()


def detect_format(text: str) -> Literal["figma", "discovery"]:
    if re.search(r"^##\s+UI Flow Test Cases\s*$", text, re.MULTILINE):
        return "figma"
    return "discovery"


def section_policy(title: str, fmt: Literal["figma", "discovery"]) -> Policy:
    t = strip_md(title).lower()
    if "automation assessment" in t:
        return "skip"
    if "requirements gaps" in t or "coverage matrix" in t:
        return "skip"
    if "priority recommendations" in t:
        return "skip"

    if fmt == "figma":
        if "ui flow" in t and "test case" in t:
            return "hp"
        if "error and edge" in t and "test case" in t:
            return "neg"
        return "skip"

    # discovery
    if "happy path" in t and "test case" in t:
        return "hp"
    if re.search(r"\bnegative\b", t) and "test case" in t:
        return "neg"
    return "skip"


def is_category_banner_row(cells: list[str]) -> bool:
    if not cells:
        return False
    a = strip_md(cells[0]).lower()
    return a in (
        "happy path",
        "edge case",
        "negative",
        "security",
        "ui flows",
        "component state",
        "layout / visual",
        "responsive",
        "accessibility",
        "error / edge",
    ) or a.endswith(" path") and "automatable" in " ".join(cells).lower()


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|"):
        return []
    parts = line.split("|")
    # leading/trailing empty from | foo | bar |
    inner = [strip_md(p) for p in parts[1:-1]] if len(parts) >= 2 else []
    if len(parts) >= 2 and parts[-1].strip() == "":
        inner = [strip_md(p) for p in parts[1:-1]]
    elif len(parts) >= 2:
        inner = [strip_md(p) for p in parts[1:]]
    return inner


def extract_issue_summary_from_markdown(markdown_text: str) -> str | None:
    """
    Jira issue Summary (title) from discovery metadata table.
    Uses regex so values containing literal pipes (markdown \\|) are not split incorrectly.
    """
    row = re.compile(
        r"^\|\s*[^|]*\bSummary\b[^|]*\|\s*(.+)\|\s*$",
        re.IGNORECASE,
    )
    for line in markdown_text.splitlines()[:80]:
        raw = line.strip()
        m = row.match(raw)
        if not m:
            continue
        val = strip_md(m.group(1).strip())
        val = val.replace("\\|", "|").strip()
        if val:
            return val[:500]
    return None


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.match(r"^[\s:-]+$", c or "") for c in cells)


def find_test_table_columns(header_cells: list[str]) -> dict[str, int] | None:
    norm = [re.sub(r"\s+", " ", c.lower()) for c in header_cells]
    mapping: dict[str, int] = {}
    for i, h in enumerate(norm):
        if h == "id":
            mapping["id"] = i
        if "scenario" in h:
            mapping["scenario"] = i
        if "precondition" in h:
            mapping["preconditions"] = i
        if h == "steps" or h.startswith("step"):
            mapping["steps"] = i
        if "expected" in h:
            mapping["expected"] = i
        if "comment" in h:
            mapping["comments"] = i
    if "id" in mapping and "scenario" in mapping:
        return mapping
    return None


def parse_tables(
    text: str,
    fmt: Literal["figma", "discovery"],
    strict: bool,
) -> list[tuple[Policy, dict[str, str]]]:
    rows_out: list[tuple[Policy, dict[str, str]]] = []
    lines = text.splitlines()
    i = 0
    in_automation = False
    h2_policy: Policy = "skip"

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        if re.match(r"^##\s+", line) and not re.match(r"^###", line):
            title = re.sub(r"^##\s+", "", line).strip()
            if re.search(r"(?i)automation\s+assessment", title):
                in_automation = True
                h2_policy = "skip"
            else:
                in_automation = False
                h2_policy = section_policy(title, fmt)
            i += 1
            continue

        if re.match(r"^###\s+", line):
            if in_automation:
                i += 1
                continue
            title = re.sub(r"^###\s+", "", line).strip()
            sub = section_policy(title, fmt)
            if sub != "skip":
                h2_policy = sub
            i += 1
            continue

        if in_automation:
            i += 1
            continue

        if line.strip().startswith("|") and h2_policy in ("hp", "neg"):
            block: list[str] = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1

            parsed = parse_single_table(block, h2_policy, strict)
            rows_out.extend(parsed)
            i = j
            continue

        i += 1

    return rows_out


def parse_single_table(
    block: list[str],
    policy: Policy,
    strict: bool,
) -> list[tuple[Policy, dict[str, str]]]:
    out: list[tuple[Policy, dict[str, str]]] = []
    if policy == "skip":
        return out

    inner_policy: Policy = policy
    colmap: dict[str, int] | None = None

    for raw in block:
        cells = split_table_row(raw)
        if not cells:
            continue
        if is_separator_row(cells):
            continue

        if colmap is None:
            cm = find_test_table_columns(cells)
            if cm is None:
                continue
            colmap = cm
            continue

        if is_category_banner_row(cells):
            # subsection inside automation-style tables only switches inner tags
            label = strip_md(cells[0]).lower()
            if label == "happy path":
                inner_policy = "hp"
            elif label == "negative":
                inner_policy = "neg"
            elif label in ("edge case", "security", "ui flows", "component state", "layout / visual", "responsive", "accessibility", "error / edge"):
                inner_policy = "skip"
            else:
                inner_policy = policy
            continue

        if inner_policy not in ("hp", "neg"):
            continue

        def get(key: str) -> str:
            idx = colmap.get(key)  # type: ignore[union-attr]
            if idx is None or idx >= len(cells):
                return ""
            return cells[idx].strip()

        tid = get("id")
        scenario = get("scenario")
        if not tid or not scenario:
            continue
        if strict and inner_policy != policy:
            # banner switched context; in strict mode only use outer section policy
            if inner_policy == "skip":
                continue

        row = {
            "id": tid,
            "scenario": scenario,
            "preconditions": get("preconditions"),
            "steps": get("steps"),
            "expected": get("expected"),
        }
        if "comments" in colmap:
            row["comments"] = get("comments")
        out.append((inner_policy, row))

    # In strict mode, ignore rows where inner_policy came only from category rows inside edge tables
    if strict:
        filtered: list[tuple[Policy, dict[str, str]]] = []
        for pol, r in out:
            if pol == policy:
                filtered.append((pol, r))
        return filtered

    return out


def build_description(
    jira_key: str | None,
    summary_text: str,
    component_label: str | None,
) -> str:
    """Zephyr Description: story context; align with Jira before import."""
    parts: list[str] = []
    if jira_key:
        parts.append(f"Jira: {jira_key}")
    if component_label:
        parts.append(f"Component (from ticket FE/BE hint): {component_label}")
    if summary_text:
        parts.append("")
        parts.append(summary_text.strip())
    return "\n".join(parts).strip()[:12000]


def build_objective(jira_key: str | None, category: Policy, row: dict[str, str]) -> str:
    """Testing objective — concise; detailed steps go in Test Script (step-by-step)."""
    lab = "Happy Path" if category == "hp" else "Negative"
    bits = []
    if jira_key:
        bits.append(f"Verify {jira_key} ({lab}): {row.get('scenario', '').strip()}")
    else:
        bits.append(f"{lab}: {row.get('scenario', '').strip()}")
    bits.append("")
    bits.append("Validate preconditions, execute the step-by-step script, and assert expected results.")
    return "\n".join(bits).strip()[:8000]


def truncate(s: str, max_len: int) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


_AC_LABEL = re.compile(
    r"\bAC\s*([\d]+(?:\.[\d]+)?(?:\s*[-–]\s*[\d]+(?:\.[\d]+)?)?)",
    re.IGNORECASE,
)


def extract_ac_bucket(comments: str, scenario: str, preconditions: str = "") -> str:
    """
    Map a discovery row to one Acceptance Criterion bucket for Zephyr (--per-ac).
    Searches optional **Comments**, then **Scenario**, then **Preconditions**, for AC 1, AC 1.2, AC 1–4.
    """
    text = f"{comments or ''} {scenario or ''} {preconditions or ''}"
    m = _AC_LABEL.search(text)
    if m:
        label = m.group(1).strip().replace("–", "-").replace("—", "-")
        return f"AC {label}"
    return "_Unmapped"


def natural_bucket_sort_key(bucket: str) -> tuple[int | float, ...]:
    if bucket == "_Unmapped":
        return (10**9,)
    nums = [int(x) for x in re.findall(r"\d+", bucket)]
    return tuple(nums) if nums else (0,)


def group_rows_by_ac(
    rows: list[tuple[Policy, dict[str, str]]],
) -> list[tuple[str, list[tuple[Policy, dict[str, str]]]]]:
    """Preserve row order within each AC group; emit groups sorted by AC label."""
    buckets: dict[str, list[tuple[Policy, dict[str, str]]]] = {}
    order: list[str] = []
    for cat, row in rows:
        comments = (row.get("comments") or "").strip()
        scenario = (row.get("scenario") or "").strip()
        pre = (row.get("preconditions") or "").strip()
        b = extract_ac_bucket(comments, scenario, pre)
        if b not in buckets:
            buckets[b] = []
            order.append(b)
        buckets[b].append((cat, row))
    ordered_labels = sorted(order, key=natural_bucket_sort_key)
    return [(lbl, buckets[lbl]) for lbl in ordered_labels]


def merge_custom_fields() -> dict:
    """
    Zephyr Scale projects may require custom fields on POST /testcases.
    Defaults match common single-select values; override with ZEPHYR_CUSTOM_FIELDS_JSON
    (full object) or ZEPHYR_CF_CAN_BE_AUTOMATED / ZEPHYR_CF_ALREADY_AUTOMATED.
    Set ZEPHYR_NO_DEFAULT_CUSTOM_FIELDS=1 to skip built-in defaults (provide JSON only).
    """
    cf: dict = {}
    raw = os.environ.get("ZEPHYR_CUSTOM_FIELDS_JSON", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                cf.update(parsed)
        except json.JSONDecodeError:
            pass
    if os.environ.get("ZEPHYR_NO_DEFAULT_CUSTOM_FIELDS") == "1":
        return cf
    if "CanBeAutomated?" not in cf:
        cf["CanBeAutomated?"] = os.environ.get("ZEPHYR_CF_CAN_BE_AUTOMATED", "Yes")
    if "AlreadyAutomated?" not in cf:
        cf["AlreadyAutomated?"] = os.environ.get("ZEPHYR_CF_ALREADY_AUTOMATED", "No")
    return cf


def build_payload(
    project_key: str,
    category: Policy,
    row: dict[str, str],
    *,
    jira_key: str | None,
    summary_text: str,
    component_label: str | None,
    owner_id: str | None,
    folder_id: str | None,
) -> dict:
    cat = "Happy Path" if category == "hp" else "Negative"
    ticket = jira_key or "NOKEY"
    name = truncate(f"{ticket} | [{cat}] {row['id']} — {row['scenario']}", 250)
    desc = build_description(jira_key, summary_text, component_label)
    body: dict = {
        "projectKey": project_key,
        "name": name,
        "objective": build_objective(jira_key, category, row),
        "precondition": (row.get("preconditions") or "")[:8000],
    }
    if desc:
        body["description"] = desc

    apply_create_tail(body, folder_id, owner_id)
    return body


def apply_create_tail(body: dict[str, Any], folder_id: str | None, owner_id: str | None) -> None:
    """Status, priority, folder, owner, component, custom fields (shared POST /testcases tail)."""
    st = os.environ.get("ZEPHYR_STATUS_NAME")
    if st is None:
        body["statusName"] = "Approved"
    elif st.strip() != "":
        body["statusName"] = st.strip()

    pr = os.environ.get("ZEPHYR_PRIORITY_NAME")
    if pr:
        body["priorityName"] = pr

    if folder_id and str(folder_id).strip().isdigit():
        body["folderId"] = int(folder_id)
    if owner_id and str(owner_id).strip():
        body["ownerId"] = str(owner_id).strip()

    cid = (os.environ.get("ZEPHYR_COMPONENT_ID") or "").strip()
    if cid.isdigit():
        body["componentId"] = int(cid)

    extra_cf = merge_custom_fields()
    if extra_cf:
        body["customFields"] = extra_cf


def build_consolidated_step_items(rows: list[tuple[Policy, dict[str, str]]]) -> list[dict[str, str]]:
    """One Test Script step per discovery row (readable in Scale UI)."""
    items: list[dict[str, str]] = []
    for cat, row in rows:
        lab = "Happy Path" if cat == "hp" else "Negative"
        rid = (row.get("id") or "").strip()
        scenario = (row.get("scenario") or "").strip()
        steps = (row.get("steps") or "").strip()
        pre = (row.get("preconditions") or "").strip()
        exp = (row.get("expected") or "").strip()
        desc = f"[{lab}] {rid} — {scenario}"
        if steps:
            desc = f"{desc}\n\n{steps}"
        items.append(
            {
                "description": truncate(desc, 8000),
                "testData": truncate(pre, 4000),
                "expectedResult": truncate(exp, 4000),
            }
        )
    return items


def build_consolidated_payload(
    project_key: str,
    rows: list[tuple[Policy, dict[str, str]]],
    *,
    jira_key: str | None,
    summary_text: str,
    component_label: str | None,
    owner_id: str | None,
    folder_id: str | None,
    story_name: str | None = None,
    ac_bucket: str | None = None,
) -> dict:
    """Single Zephyr test case representing the whole HP+NEG pack (or one AC slice when ac_bucket set)."""
    ticket = jira_key or "NOKEY"
    n = len(rows)
    ab = (ac_bucket or "").strip()
    if ab and ab != "_Unmapped":
        if story_name and story_name.strip():
            name = truncate(f"{story_name.strip()} — {ab}", 250)
        else:
            name = truncate(
                f"{ticket} | {ab} — Happy Path + Negative ({n} scenarios)",
                250,
            )
    elif ab == "_Unmapped":
        if story_name and story_name.strip():
            name = truncate(f"{story_name.strip()} — Unmapped (no AC tag in Scenario/Preconditions/Comments)", 250)
        else:
            name = truncate(
                f"{ticket} | Unmapped — Happy Path + Negative ({n} scenarios)",
                250,
            )
    elif story_name and story_name.strip():
        name = truncate(story_name.strip(), 250)
    else:
        name = truncate(
            f"{ticket} | Manual pack — Happy Path + Negative ({n} scenarios, consolidated)",
            250,
        )
    desc = build_description(jira_key, summary_text, component_label)
    if ab and ab != "_Unmapped":
        suffix = (
            "\n\n---\n**Per-AC import:** this Zephyr test case covers **"
            + ab
            + "** only. Each **Test Script** step = one discovery row (HP-* / NEG-*); AC grouping uses Comments (legacy), Scenario, or Preconditions."
        )
    elif ab == "_Unmapped":
        suffix = (
            "\n\n---\n**Per-AC import:** rows did not match an `AC …` label in Scenario, Preconditions, or Comments — "
            "grouped as **Unmapped**. Add AC tags for clearer splits."
        )
    else:
        suffix = (
            "\n\n---\n**Consolidated import:** one Zephyr test case; each **Test Script** step = one discovery row (HP-* / NEG-*)."
        )
    if desc:
        desc = (desc + suffix).strip()[:12000]
    else:
        desc = suffix.strip()[:12000]

    if ab and ab != "_Unmapped":
        objective = (
            f"For {ticket}, verify **{ab}**: execute all {n} listed scenarios in order for this acceptance criterion. "
            "Each step states one discovery case; satisfy preconditions (Test data) before executing that step; "
            "assert the Expected result."
        )[:8000]
    else:
        objective = (
            f"For {ticket}, execute all {n} listed scenarios in order. Each step states one discovery case; "
            "satisfy preconditions (Test data) before executing that step; assert the Expected result."
        )[:8000]
    precondition = (
        "Environment and credentials support this story. Row-level preconditions appear in **Test data** on each step."
    )[:8000]

    body: dict[str, Any] = {
        "projectKey": project_key,
        "name": name,
        "objective": objective,
        "precondition": precondition,
        "description": desc,
    }
    apply_create_tail(body, folder_id, owner_id)
    return body


def http_get(url: str, headers: dict[str, str]) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, err_body


def ensure_cloud_bearer_ready(project_key: str) -> tuple[str | None, int]:
    """
    Before POSTing test cases: require ZEPHYR_ACCESS_TOKEN and validate with GET /testcases.
    Scale Cloud does not expose a token-minting API; tokens are created in Jira UI.
    Returns (token, 0) on success, (None, 2) on failure.
    """
    token = (os.environ.get("ZEPHYR_ACCESS_TOKEN") or os.environ.get("ZEPHYR_SCALE_TOKEN") or "").strip()
    if not token:
        print(
            "Missing ZEPHYR_ACCESS_TOKEN (or ZEPHYR_SCALE_TOKEN).\n"
            "  In Jira: Zephyr Scale → API access tokens (wording may vary) → create token → set in .env.\n"
            "  Validate anytime: python .cursor/skills/zephyr-scale/scripts/zephyr_request.py ping",
            file=sys.stderr,
        )
        return None, 2
    base = os.environ.get("ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2").rstrip("/")
    q = urllib.parse.urlencode({"projectKey": project_key, "maxResults": "1", "startAt": "0"})
    url = f"{base}/testcases?{q}"
    status, body = http_get(url, {"Authorization": f"Bearer {token}", "Accept": "application/json"})
    if status == 401:
        print(
            "Zephyr Scale returned 401 Unauthorized — token invalid or revoked.\n"
            "  Create a new API access token in Jira (Zephyr Scale) and update ZEPHYR_ACCESS_TOKEN in .env, then retry.",
            file=sys.stderr,
        )
        return None, 2
    if status == 403:
        print(
            "Zephyr Scale returned 403 Forbidden on preflight. Check ZEPHYR_PROJECT_KEY and token scopes.\n"
            f"  Body (truncated): {body[:1200]}",
            file=sys.stderr,
        )
        return None, 2
    if status != 200:
        print(f"Zephyr Cloud preflight failed HTTP {status}: {body[:2000]}", file=sys.stderr)
        return None, 2
    return token, 0


def http_post_json(url: str, headers: dict[str, str], payload: dict) -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    h = {**headers, "Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, err_body


def post_teststeps_cloud(
    base: str, headers: dict[str, str], test_case_key: str, items: list[dict[str, str]]
) -> tuple[int, str]:
    """POST step-by-step test script (inline steps)."""
    url = f"{base.rstrip('/')}/testcases/{urllib.parse.quote(test_case_key, safe='')}/teststeps"
    payload: dict[str, Any] = {"mode": "OVERWRITE", "items": [{"inline": it} for it in items]}
    return http_post_json(url, headers, payload)


def post_issue_link_cloud(
    base: str, headers: dict[str, str], test_case_key: str, issue_id: str
) -> tuple[int, str]:
    """Traceability: link test case to Jira user story / issue (numeric id)."""
    url = f"{base.rstrip('/')}/testcases/{urllib.parse.quote(test_case_key, safe='')}/links/issues"
    try:
        jid: int | str = int(str(issue_id).strip())
    except ValueError:
        jid = issue_id.strip()
    return http_post_json(url, headers, {"issueId": jid})


def import_rows_consolidated(
    rows: list[tuple[Policy, dict[str, str]]],
    dry_run: bool,
    *,
    markdown_full: str,
    jira_key: str | None,
    summary_text: str,
    owner_id: str | None,
    folder_id: str | None,
    issue_numeric_id: str | None,
    story_name: str | None = None,
) -> int:
    """Create one Zephyr Cloud test case; Test Script = one step per discovery row."""
    mode = (os.environ.get("ZEPHYR_DEPLOYMENT") or "").strip().lower()
    if not mode:
        mode = "server" if os.environ.get("ZEPHYR_JIRA_BASE_URL") else "cloud"
    if mode != "cloud":
        print(
            "Consolidated import (--single-testcase) is only supported for Zephyr Scale Cloud.",
            file=sys.stderr,
        )
        return 2

    project = os.environ.get("ZEPHYR_PROJECT_KEY")
    if not project:
        print("Missing ZEPHYR_PROJECT_KEY", file=sys.stderr)
        return 2

    component_label = infer_component_label(markdown_full)
    cloud_base = os.environ.get("ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2").rstrip("/")
    url_base = f"{cloud_base}/testcases"

    step_items = build_consolidated_step_items(rows)
    payload = build_consolidated_payload(
        project,
        rows,
        jira_key=jira_key,
        summary_text=summary_text,
        component_label=component_label,
        owner_id=owner_id,
        folder_id=folder_id,
        story_name=story_name,
        ac_bucket=None,
    )

    if dry_run:
        preview_items = [{"inline": it} for it in step_items[:2]]
        if len(step_items) > 2:
            preview_items.append(
                {
                    "inline": {
                        "description": f"(… {len(step_items) - 2} more step(s) omitted in preview …)",
                        "testData": "",
                        "expectedResult": "",
                    }
                }
            )
        plan: dict[str, Any] = {
            "mode": "single-testcase",
            "create_testcase": {"url": url_base, "payload": payload},
            "test_script_step_by_step": {
                "url_suffix": "/testcases/<KEY>/teststeps",
                "step_count": len(step_items),
                "payload_preview": {"mode": "OVERWRITE", "items": preview_items},
            },
        }
        if issue_numeric_id:
            plan["traceability_issue"] = {
                "url_suffix": "/testcases/<KEY>/links/issues",
                "payload": {"issueId": issue_numeric_id},
            }
        print(json.dumps(plan, ensure_ascii=False, indent=2)[:24000])
        print(f"Dry-run: 1 test case with {len(step_items)} Test Script step(s).")
        return 0

    token, pre_rc = ensure_cloud_bearer_ready(project)
    if pre_rc != 0:
        return pre_rc
    if not owner_id or not folder_id:
        print(
            "Cloud import requires Zephyr owner and folder.\n"
            "  Set ZEPHYR_OWNER_ID and ZEPHYR_FOLDER_ID or pass --owner-id and --folder-id.",
            file=sys.stderr,
        )
        return 2
    headers = {"Authorization": f"Bearer {token}"}
    skip_link = os.environ.get("ZEPHYR_SKIP_ISSUE_LINK", "").strip() in ("1", "true", "yes")
    if not issue_numeric_id and not skip_link:
        print(
            "Traceability requires Jira numeric issue id.\n"
            "  Set ZEPHYR_JIRA_ISSUE_ID, or JIRA_CLOUD_URL + JIRA_API_MAIL + JIRA_API_KEY,\n"
            "  or ZEPHYR_SKIP_ISSUE_LINK=1.",
            file=sys.stderr,
        )
        return 2

    status, body = http_post_json(url_base, headers, payload)
    if status not in (200, 201):
        print(f"HTTP {status} consolidated create: {body[:2000]}", file=sys.stderr)
        return 1
    try:
        data = json.loads(body)
        tc_key = data.get("key") or data.get("id")
    except json.JSONDecodeError:
        print(f"Create returned non-JSON: {body[:500]}", file=sys.stderr)
        return 1

    tc_str = str(tc_key) if tc_key is not None else ""
    if not tc_str:
        print("Create response missing test case key.", file=sys.stderr)
        return 1

    st2, body2 = post_teststeps_cloud(cloud_base, headers, tc_str, step_items)
    if st2 not in (200, 201):
        print(f"Test steps HTTP {st2} for {tc_key}: {body2[:2000]}", file=sys.stderr)
        return 1
    if issue_numeric_id and not skip_link:
        st3, body3 = post_issue_link_cloud(cloud_base, headers, tc_str, str(issue_numeric_id))
        if st3 not in (200, 201):
            print(f"Issue link HTTP {st3} for {tc_key}: {body3[:2000]}", file=sys.stderr)
            return 1
    link_note = " (issue link applied)" if issue_numeric_id and not skip_link else ""
    print(f"Created: consolidated manual pack -> {tc_str} ({len(step_items)} steps{link_note})")
    return 0


def import_rows_per_ac(
    rows: list[tuple[Policy, dict[str, str]]],
    dry_run: bool,
    *,
    markdown_full: str,
    jira_key: str | None,
    summary_text: str,
    owner_id: str | None,
    folder_id: str | None,
    issue_numeric_id: str | None,
    story_name: str | None = None,
) -> int:
    """Create one Zephyr Cloud test case per Acceptance Criterion bucket (from Scenario / Preconditions / Comments)."""
    mode = (os.environ.get("ZEPHYR_DEPLOYMENT") or "").strip().lower()
    if not mode:
        mode = "server" if os.environ.get("ZEPHYR_JIRA_BASE_URL") else "cloud"
    if mode != "cloud":
        print(
            "Per-AC import (--per-ac) is only supported for Zephyr Scale Cloud.",
            file=sys.stderr,
        )
        return 2

    project = os.environ.get("ZEPHYR_PROJECT_KEY")
    if not project:
        print("Missing ZEPHYR_PROJECT_KEY", file=sys.stderr)
        return 2

    groups = group_rows_by_ac(rows)
    if len(groups) == 1 and groups[0][0] == "_Unmapped" and len(rows) > 1:
        print(
            "Warning: --per-ac did not find AC labels (e.g. AC 1, AC 1.2) in Scenario, Preconditions, or Comments; "
            "all rows are in one **Unmapped** case. Add **AC …** to Scenario or Preconditions for a per-AC split.",
            file=sys.stderr,
        )

    component_label = infer_component_label(markdown_full)
    cloud_base = os.environ.get("ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2").rstrip("/")
    url_base = f"{cloud_base}/testcases"

    if dry_run:
        plans: list[dict[str, Any]] = []
        for ac_bucket, grp in groups:
            step_items = build_consolidated_step_items(grp)
            payload = build_consolidated_payload(
                project,
                grp,
                jira_key=jira_key,
                summary_text=summary_text,
                component_label=component_label,
                owner_id=owner_id,
                folder_id=folder_id,
                story_name=story_name,
                ac_bucket=ac_bucket,
            )
            entry: dict[str, Any] = {
                "ac_bucket": ac_bucket,
                "step_count": len(step_items),
                "create_testcase": {"url": url_base, "payload": payload},
            }
            if issue_numeric_id:
                entry["traceability_issue"] = {"issueId": issue_numeric_id}
            plans.append(entry)
        print(json.dumps({"mode": "per-ac", "cases": plans}, ensure_ascii=False, indent=2)[:48000])
        print(f"Dry-run: {len(groups)} test case(s) (one per AC bucket).")
        return 0

    token, pre_rc = ensure_cloud_bearer_ready(project)
    if pre_rc != 0:
        return pre_rc
    if not owner_id or not folder_id:
        print(
            "Cloud import requires Zephyr owner and folder.\n"
            "  Set ZEPHYR_OWNER_ID and ZEPHYR_FOLDER_ID or pass --owner-id and --folder-id.",
            file=sys.stderr,
        )
        return 2
    headers = {"Authorization": f"Bearer {token}"}
    skip_link = os.environ.get("ZEPHYR_SKIP_ISSUE_LINK", "").strip() in ("1", "true", "yes")
    if not issue_numeric_id and not skip_link:
        print(
            "Traceability requires Jira numeric issue id.\n"
            "  Set ZEPHYR_JIRA_ISSUE_ID, or JIRA_CLOUD_URL + JIRA_API_MAIL + JIRA_API_KEY,\n"
            "  or ZEPHYR_SKIP_ISSUE_LINK=1.",
            file=sys.stderr,
        )
        return 2

    created_keys: list[str] = []
    for ac_bucket, grp in groups:
        step_items = build_consolidated_step_items(grp)
        payload = build_consolidated_payload(
            project,
            grp,
            jira_key=jira_key,
            summary_text=summary_text,
            component_label=component_label,
            owner_id=owner_id,
            folder_id=folder_id,
            story_name=story_name,
            ac_bucket=ac_bucket,
        )
        status, body = http_post_json(url_base, headers, payload)
        if status not in (200, 201):
            print(f"HTTP {status} per-AC create ({ac_bucket}): {body[:2000]}", file=sys.stderr)
            return 1
        try:
            data = json.loads(body)
            tc_key = data.get("key") or data.get("id")
        except json.JSONDecodeError:
            print(f"Create returned non-JSON for {ac_bucket}: {body[:500]}", file=sys.stderr)
            return 1
        tc_str = str(tc_key) if tc_key is not None else ""
        if not tc_str:
            print(f"Create response missing test case key for {ac_bucket}.", file=sys.stderr)
            return 1

        st2, body2 = post_teststeps_cloud(cloud_base, headers, tc_str, step_items)
        if st2 not in (200, 201):
            print(f"Test steps HTTP {st2} for {tc_key} ({ac_bucket}): {body2[:2000]}", file=sys.stderr)
            return 1
        if issue_numeric_id and not skip_link:
            st3, body3 = post_issue_link_cloud(cloud_base, headers, tc_str, str(issue_numeric_id))
            if st3 not in (200, 201):
                print(f"Issue link HTTP {st3} for {tc_key}: {body3[:2000]}", file=sys.stderr)
                return 1
        created_keys.append(tc_str)
        link_note = " (issue link applied)" if issue_numeric_id and not skip_link else ""
        print(f"Created: {ac_bucket} -> {tc_str} ({len(step_items)} steps{link_note})")

    print(f"Done. {len(created_keys)} test case(s) (per Acceptance Criterion).")
    return 0


def import_rows(
    rows: list[tuple[Policy, dict[str, str]]],
    dry_run: bool,
    *,
    markdown_full: str,
    jira_key: str | None,
    summary_text: str,
    owner_id: str | None,
    folder_id: str | None,
    issue_numeric_id: str | None,
) -> int:
    mode = (os.environ.get("ZEPHYR_DEPLOYMENT") or "").strip().lower()
    if not mode:
        mode = "server" if os.environ.get("ZEPHYR_JIRA_BASE_URL") else "cloud"

    project = os.environ.get("ZEPHYR_PROJECT_KEY")
    if not project:
        print("Missing ZEPHYR_PROJECT_KEY", file=sys.stderr)
        return 2

    component_label = infer_component_label(markdown_full)

    cloud_base = ""
    if mode == "server":
        jira = (os.environ.get("ZEPHYR_JIRA_BASE_URL") or "").rstrip("/")
        if dry_run and not jira:
            jira = "https://jira.example.invalid"
        url_base = f"{jira}/rest/atm/1.0/testcase" if jira else ""
    else:
        cloud_base = os.environ.get("ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2").rstrip("/")
        url_base = f"{cloud_base}/testcases"

    if dry_run:
        for cat, row in rows:
            payload = build_payload(
                project,
                cat,
                row,
                jira_key=jira_key,
                summary_text=summary_text,
                component_label=component_label,
                owner_id=owner_id,
                folder_id=folder_id,
            )
            step_items = split_step_items(row.get("steps") or "", row.get("preconditions") or "", row.get("expected") or "")
            plan = {
                "create_testcase": {"url": url_base, "payload": payload},
                "test_script_step_by_step": {
                    "url_suffix": f"/testcases/<KEY>/teststeps",
                    "payload": {"mode": "OVERWRITE", "items": [{"inline": it} for it in step_items]},
                },
            }
            if issue_numeric_id and mode == "cloud":
                plan["traceability_issue"] = {
                    "url_suffix": f"/testcases/<KEY>/links/issues",
                    "payload": {"issueId": issue_numeric_id},
                }
            print(json.dumps(plan, ensure_ascii=False, indent=2)[:16000])
        print(f"Dry-run complete. {len(rows)} test case(s) planned (folder/owner/issue shown if provided).")
        return 0

    if mode == "cloud":
        token, pre_rc = ensure_cloud_bearer_ready(project)
        if pre_rc != 0:
            return pre_rc
        if not owner_id or not folder_id:
            print(
                "Cloud import requires Zephyr owner and folder.\n"
                "  Set ZEPHYR_OWNER_ID (Atlassian account id) and ZEPHYR_FOLDER_ID (numeric),\n"
                "  or pass --owner-id and --folder-id.\n"
                "  Confirm with the test lead before creating cases.",
                file=sys.stderr,
            )
            return 2
        headers = {"Authorization": f"Bearer {token}"}
        skip_link = os.environ.get("ZEPHYR_SKIP_ISSUE_LINK", "").strip() in ("1", "true", "yes")
        if not issue_numeric_id and not skip_link:
            print(
                "Traceability requires Jira numeric issue id.\n"
                "  Set ZEPHYR_JIRA_ISSUE_ID, or set JIRA_CLOUD_URL + JIRA_API_MAIL + JIRA_API_KEY\n"
                "  (or JIRA_API_EMAIL + JIRA_API_TOKEN) so the story key can be resolved.\n"
                "  Or set ZEPHYR_SKIP_ISSUE_LINK=1 to create cases without a link (not recommended).",
                file=sys.stderr,
            )
            return 2
    elif mode == "server":
        jira = os.environ.get("ZEPHYR_JIRA_BASE_URL", "").rstrip("/")
        user = os.environ.get("ZEPHYR_JIRA_USER") or os.environ.get("JIRA_USERNAME")
        password = os.environ.get("ZEPHYR_JIRA_PASSWORD") or os.environ.get("JIRA_PASSWORD")
        if not jira or not user or not password:
            print("Missing Server/DC Jira URL or credentials", file=sys.stderr)
            return 2
        raw = f"{user}:{password}".encode("utf-8")
        basic = base64.b64encode(raw).decode("ascii")
        headers = {"Authorization": f"Basic {basic}"}
        if not url_base:
            print("Missing ZEPHYR_JIRA_BASE_URL for Server/DC.", file=sys.stderr)
            return 2
        print("Server/DC mode: creating base test cases only; verify teststeps/links APIs separately.", file=sys.stderr)

    ok = 0
    for cat, row in rows:
        payload = build_payload(
            project,
            cat,
            row,
            jira_key=jira_key,
            summary_text=summary_text,
            component_label=component_label,
            owner_id=owner_id,
            folder_id=folder_id,
        )
        status, body = http_post_json(url_base, headers, payload)
        if status not in (200, 201):
            print(f"HTTP {status} for {row.get('id')}: {body[:2000]}", file=sys.stderr)
            return 1
        try:
            data = json.loads(body)
            tc_key = data.get("key") or data.get("id")
        except json.JSONDecodeError:
            print(f"Create returned non-JSON for {row.get('id')}: {body[:500]}", file=sys.stderr)
            return 1

        tc_str = str(tc_key) if tc_key is not None else ""
        if mode == "cloud" and cloud_base and tc_str:
            step_items = split_step_items(
                row.get("steps") or "",
                row.get("preconditions") or "",
                row.get("expected") or "",
            )
            st2, body2 = post_teststeps_cloud(cloud_base, headers, tc_str, step_items)
            if st2 not in (200, 201):
                print(f"Test steps HTTP {st2} for {tc_key}: {body2[:2000]}", file=sys.stderr)
                return 1
            skip_link = os.environ.get("ZEPHYR_SKIP_ISSUE_LINK", "").strip() in ("1", "true", "yes")
            if issue_numeric_id and not skip_link:
                st3, body3 = post_issue_link_cloud(cloud_base, headers, tc_str, str(issue_numeric_id))
                if st3 not in (200, 201):
                    print(f"Issue link HTTP {st3} for {tc_key}: {body3[:2000]}", file=sys.stderr)
                    return 1
        print(
            f"Created: {row.get('id')} -> {tc_str} (steps + link applied)"
            if mode == "cloud"
            else f"Created: {row.get('id')} -> {tc_str or tc_key}"
        )
        ok += 1
    print(f"Done. {ok} test case(s).")
    return 0


def main() -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="Import discovery Markdown into Zephyr Scale (HP + Neg only)")
    p.add_argument("markdown_file", type=Path, help="Path to test-cases .md")
    p.add_argument("--dry-run", action="store_true", help="Parse only; print planned API payloads")
    p.add_argument("--strict", action="store_true", help="Ignore inner category rows that change policy")
    p.add_argument("--jira-key", default=None, help="Story key, e.g. HBGDIGI-1978 (else inferred from filename / **Jira:** line)")
    p.add_argument("--owner-id", default=None, help="Zephyr owner: Atlassian account id (or ZEPHYR_OWNER_ID)")
    p.add_argument("--folder-id", default=None, help="Zephyr folder numeric id (or ZEPHYR_FOLDER_ID)")
    p.add_argument("--jira-issue-id", default=None, help="Numeric Jira issue id for traceability (or ZEPHYR_JIRA_ISSUE_ID)")
    mode_grp = p.add_mutually_exclusive_group()
    mode_grp.add_argument(
        "--per-ac",
        action="store_true",
        help="Cloud only (recommended): one Zephyr test case per Acceptance Criterion — rows grouped by AC in Scenario / Preconditions / Comments (AC 1, AC 1.2, …)",
    )
    mode_grp.add_argument(
        "--single-testcase",
        action="store_true",
        help="Cloud only: one Zephyr test case for the whole story; each HP/NEG row becomes one Test Script step",
    )
    args = p.parse_args()

    path: Path = args.markdown_file
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    fmt = detect_format(text)
    rows = parse_tables(text, fmt, strict=args.strict)

    # Drop duplicates by (id, scenario) keeping first
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[Policy, dict[str, str]]] = []
    for cat, r in rows:
        k = (r["id"], r["scenario"])
        if k in seen:
            continue
        seen.add(k)
        unique.append((cat, r))

    if not unique:
        print("No happy path / negative rows found. Check section headings and table columns.", file=sys.stderr)
        print(f"Detected format: {fmt}", file=sys.stderr)
        return 1

    jira_key = (args.jira_key or os.environ.get("ZEPHYR_JIRA_KEY") or "").strip() or extract_jira_key(text, path.name)
    summary_text = extract_summary_section(text)
    component_label = infer_component_label(text)
    owner_id = (args.owner_id or os.environ.get("ZEPHYR_OWNER_ID") or "").strip() or None
    folder_id = (args.folder_id or os.environ.get("ZEPHYR_FOLDER_ID") or "").strip() or None
    explicit_issue = (args.jira_issue_id or os.environ.get("ZEPHYR_JIRA_ISSUE_ID") or "").strip() or None
    issue_numeric_id, jira_summary = resolve_jira_issue_for_import(jira_key, explicit_issue)
    md_story_title = extract_issue_summary_from_markdown(text)
    story_name = ((jira_summary or "").strip() or (md_story_title or "").strip() or None)

    print(
        f"Parsed {len(unique)} row(s); format={fmt}; dry_run={args.dry_run}; "
        f"per_ac={args.per_ac}; single_testcase={args.single_testcase}"
    )
    print("--- Preflight (align with story before creating in Zephyr) ---")
    print(f"  Jira story key: {jira_key or '(not set — add --jira-key or rename file test-cases-KEY.md)'}")
    if args.per_ac:
        grp_preview = group_rows_by_ac(unique)
        labels = ", ".join(g[0] for g in grp_preview)
        print(f"  Per-AC mode: {len(grp_preview)} Zephyr case(s) — buckets: {labels}")
        zbase = story_name or f"{jira_key or 'NOKEY'} | Manual pack (fallback)"
        print(f"  Name pattern: `{zbase} — AC …` (from Jira Summary + AC label)")
    elif args.single_testcase:
        zname = story_name or f"{jira_key or 'NOKEY'} | Manual pack — Happy Path + Negative (fallback)"
        print(f"  Consolidated Zephyr test case name (Jira Summary / metadata): {zname}")
    print(f"  Description source: ## Summary section ({len(summary_text)} chars)")
    print(f"  Objective / Precondition: per test row + story key in objective")
    print(f"  Status: Approved (override with ZEPHYR_STATUS_NAME, or set to empty string to omit)")
    print(f"  Component hint from ticket (FE/BE): {component_label or '(none — set ZEPHYR_COMPONENT_ID if Scale uses component id)'}")
    print(f"  Zephyr folder id: {folder_id or '(missing — required for Cloud import)'}")
    print(f"  Zephyr owner id: {owner_id or '(missing — confirm with owner before import)'}")
    print(f"  Traceability Jira issue id: {issue_numeric_id or '(not resolved — set ZEPHYR_JIRA_ISSUE_ID or JIRA_CLOUD_URL + JIRA_API_MAIL + JIRA_API_KEY)'}")
    print("--- End preflight ---")

    if args.single_testcase:
        return import_rows_consolidated(
            unique,
            dry_run=args.dry_run,
            markdown_full=text,
            jira_key=jira_key,
            summary_text=summary_text,
            owner_id=owner_id,
            folder_id=folder_id,
            issue_numeric_id=issue_numeric_id,
            story_name=story_name,
        )
    if args.per_ac:
        return import_rows_per_ac(
            unique,
            dry_run=args.dry_run,
            markdown_full=text,
            jira_key=jira_key,
            summary_text=summary_text,
            owner_id=owner_id,
            folder_id=folder_id,
            issue_numeric_id=issue_numeric_id,
            story_name=story_name,
        )
    return import_rows(
        unique,
        dry_run=args.dry_run,
        markdown_full=text,
        jira_key=jira_key,
        summary_text=summary_text,
        owner_id=owner_id,
        folder_id=folder_id,
        issue_numeric_id=issue_numeric_id,
    )


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Minimal Zephyr Scale HTTP helper for private Cloud or Server/DC.

Loads .env from: this script's parent dir (skill dir), cwd, or paths in ZEPHYR_ENV_FILE.

Usage:
  python zephyr_request.py ping

Requires: Python 3.9+ (stdlib only).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_dotenv() -> None:
    """Populate os.environ from first .env found (do not override existing)."""
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


def http_get(url: str, headers: dict[str, str]) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, err_body


def ping_cloud() -> int:
    base = os.environ.get("ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2").rstrip("/")
    token = os.environ.get("ZEPHYR_ACCESS_TOKEN") or os.environ.get("ZEPHYR_SCALE_TOKEN")
    project = os.environ.get("ZEPHYR_PROJECT_KEY")
    if not token:
        print("Missing ZEPHYR_ACCESS_TOKEN (or ZEPHYR_SCALE_TOKEN)", file=sys.stderr)
        return 2
    if not project:
        print("Missing ZEPHYR_PROJECT_KEY for ping", file=sys.stderr)
        return 2
    q = urllib.parse.urlencode({"projectKey": project, "maxResults": "5", "startAt": "0"})
    url = f"{base}/testcases?{q}"
    status, body = http_get(url, {"Authorization": f"Bearer {token}", "Accept": "application/json"})
    print(f"HTTP {status}")
    try:
        data = json.loads(body)
        print(json.dumps(data, indent=2)[:8000])
    except json.JSONDecodeError:
        print(body[:8000])
    return 0 if status == 200 else 1


def ping_server() -> int:
    jira = os.environ.get("ZEPHYR_JIRA_BASE_URL", "").rstrip("/")
    user = os.environ.get("ZEPHYR_JIRA_USER") or os.environ.get("JIRA_USERNAME")
    password = os.environ.get("ZEPHYR_JIRA_PASSWORD") or os.environ.get("JIRA_PASSWORD")
    project = os.environ.get("ZEPHYR_PROJECT_KEY")
    if not jira:
        print("Missing ZEPHYR_JIRA_BASE_URL", file=sys.stderr)
        return 2
    if not user or not password:
        print("Missing ZEPHYR_JIRA_USER / ZEPHYR_JIRA_PASSWORD (or JIRA_USERNAME / JIRA_PASSWORD)", file=sys.stderr)
        return 2
    if not project:
        print("Missing ZEPHYR_PROJECT_KEY for ping", file=sys.stderr)
        return 2
    raw = f"{user}:{password}".encode("utf-8")
    basic = base64.b64encode(raw).decode("ascii")
    q = urllib.parse.urlencode({"projectKey": project, "maxResults": "5", "startAt": "0"})
    url = f"{jira}/rest/atm/1.0/testcase?{q}"
    status, body = http_get(
        url,
        {"Authorization": f"Basic {basic}", "Accept": "application/json"},
    )
    print(f"HTTP {status}")
    try:
        data = json.loads(body)
        print(json.dumps(data, indent=2)[:8000])
    except json.JSONDecodeError:
        print(body[:8000])
    return 0 if status == 200 else 1


def main() -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="Zephyr Scale minimal HTTP helper")
    p.add_argument("command", choices=["ping"], help="ping: authenticated GET smoke test")
    args = p.parse_args()

    mode = (os.environ.get("ZEPHYR_DEPLOYMENT") or "").strip().lower()
    if not mode:
        mode = "server" if os.environ.get("ZEPHYR_JIRA_BASE_URL") else "cloud"

    if args.command == "ping":
        if mode == "server":
            return ping_server()
        return ping_cloud()

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

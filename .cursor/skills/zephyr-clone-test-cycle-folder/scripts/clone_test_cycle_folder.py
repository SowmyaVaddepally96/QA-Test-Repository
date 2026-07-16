#!/usr/bin/env python3
"""
Clone a Zephyr Scale TEST_CYCLE folder tree (subfolders + test cycles + test case assignments).

Zephyr Scale Cloud has no native folder clone API; this script recreates the hierarchy via:
  POST /folders
  POST /testcycles
  POST /testexecutions  (one per test case in each cycle; status reset to Not Executed)

Usage:
  python clone_test_cycle_folder.py \\
    --source-folder-name "Regression 2026MAR17" \\
    --new-folder-name "Regression 2026MAY28" \\
    --dry-run

Environment: same as zephyr-scale skill (ZEPHYR_ACCESS_TOKEN, ZEPHYR_PROJECT_KEY, etc.).
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Subfolders with these names are created but their test cycles are not cloned.
DEFAULT_SKIP_CYCLE_FOLDER_NAMES = frozenset({"Automation"})


def load_dotenv() -> None:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / ".env",
        here.parent.parent / "zephyr-scale" / ".env",
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
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
        break


@dataclass
class FolderNode:
    id: int
    name: str
    parent_id: int | None
    children: list["FolderNode"] = field(default_factory=list)


class ZephyrClient:
    def __init__(self, base_url: str, token: str, project_key: str) -> None:
        self.base = base_url.rstrip("/")
        self.token = token
        self.project_key = project_key

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> tuple[int, Any]:
        q = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self.base}{path}{q}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        last_err: Exception | None = None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    raw = resp.read().decode("utf-8")
                    return resp.status, json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                if e.code == 429 and attempt < retries - 1:
                    wait = 60
                    m = re.search(r"Retry-After:\s*(\d+)", str(e.headers) if e.headers else "", re.I)
                    if m:
                        wait = int(m.group(1))
                    time.sleep(wait)
                    last_err = e
                    continue
                try:
                    payload = json.loads(err_body)
                except json.JSONDecodeError:
                    payload = {"message": err_body[:500]}
                return e.code, payload
            except urllib.error.URLError as e:
                last_err = e
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
        if last_err:
            raise last_err
        raise RuntimeError("request failed")

    def paginate(self, path: str, params: dict[str, str]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        start = 0
        page_size = int(params.get("maxResults", "100"))
        while True:
            p = dict(params)
            p["startAt"] = str(start)
            status, data = self.request("GET", path, params=p)
            if status != 200:
                raise RuntimeError(f"GET {path} failed HTTP {status}: {data}")
            batch = data.get("values") or []
            items.extend(batch)
            if data.get("isLast", True) or not batch:
                break
            start += page_size
        return items

    def list_test_cycle_folders(self) -> list[dict[str, Any]]:
        return self.paginate(
            "/folders",
            {
                "projectKey": self.project_key,
                "folderType": "TEST_CYCLE",
                "maxResults": "100",
            },
        )

    def list_cycles_in_folder(self, folder_id: int) -> list[dict[str, Any]]:
        return self.paginate(
            "/testcycles",
            {
                "projectKey": self.project_key,
                "folderId": str(folder_id),
                "maxResults": "100",
            },
        )

    def list_executions_in_cycle(self, cycle_key: str) -> list[dict[str, Any]]:
        return self.paginate(
            "/testexecutions",
            {"testCycle": cycle_key, "maxResults": "100"},
        )


def test_case_key_from_execution(ex: dict[str, Any]) -> str | None:
    tc = ex.get("testCase") or {}
    self_url = tc.get("self") or ""
    m = re.search(r"/testcases/([^/]+)/", self_url)
    if m:
        return m.group(1)
    key = tc.get("key")
    return str(key) if key else None


def build_subtree(all_folders: list[dict[str, Any]], root_id: int) -> FolderNode:
    by_id = {int(f["id"]): f for f in all_folders}
    if root_id not in by_id:
        raise ValueError(f"Root folder id {root_id} not found")

    nodes: dict[int, FolderNode] = {}
    for fid, raw in by_id.items():
        nodes[fid] = FolderNode(
            id=fid,
            name=raw["name"],
            parent_id=int(raw["parentId"]) if raw.get("parentId") is not None else None,
        )

    # Collect descendants of root
    subtree_ids: set[int] = {root_id}
    queue = deque([root_id])
    while queue:
        cur = queue.popleft()
        for fid, node in nodes.items():
            if node.parent_id == cur and fid not in subtree_ids:
                subtree_ids.add(fid)
                queue.append(fid)

    root = nodes[root_id]
    for fid in subtree_ids:
        if fid == root_id:
            continue
        parent = nodes[nodes[fid].parent_id]  # type: ignore[arg-type]
        parent.children.append(nodes[fid])
    for node in nodes.values():
        node.children.sort(key=lambda n: n.name.lower())
    return root


def walk_folders_bfs(root: FolderNode) -> list[FolderNode]:
    out: list[FolderNode] = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        out.append(node)
        queue.extend(node.children)
    return out


def find_folders_by_name(folders: list[dict[str, Any]], name: str, *, ignore_case: bool) -> list[dict[str, Any]]:
    if ignore_case:
        target = name.casefold()
        return [f for f in folders if (f.get("name") or "").casefold() == target]
    return [f for f in folders if f.get("name") == name]


def should_skip_cycles(folder_name: str, skip_names: set[str], *, ignore_case: bool) -> bool:
    if not skip_names:
        return False
    if ignore_case:
        return folder_name.casefold() in {n.casefold() for n in skip_names}
    return folder_name in skip_names


def resolve_skip_cycle_folder_names(
    skip_args: list[str] | None,
    *,
    include_automation_cycles: bool,
) -> set[str]:
    """Build skip set from CLI. Default: skip cycles in folder named Automation."""
    if skip_args is not None:
        return set(skip_args)
    names = set(DEFAULT_SKIP_CYCLE_FOLDER_NAMES)
    if include_automation_cycles:
        names.discard("Automation")
    return names


def plan_clone(
    client: ZephyrClient,
    source_root: FolderNode,
    *,
    skip_cycle_folder_names: set[str],
    ignore_case: bool,
) -> dict[str, Any]:
    """Build clone plan: folders, cycles, execution counts."""
    folder_order = walk_folders_bfs(source_root)
    plan: dict[str, Any] = {
        "folders": [],
        "cycles": [],
        "cycles_skipped": [],
        "execution_count": 0,
        "skip_cycle_folder_names": sorted(skip_cycle_folder_names),
    }
    for folder in folder_order:
        cycles = client.list_cycles_in_folder(folder.id)
        skip = should_skip_cycles(folder.name, skip_cycle_folder_names, ignore_case=ignore_case)
        cycle_details = []
        exec_total = 0
        if skip:
            for c in cycles:
                execs = client.list_executions_in_cycle(c["key"])
                plan["cycles_skipped"].append(
                    {
                        "source_folder_id": folder.id,
                        "source_folder_name": folder.name,
                        "source_key": c["key"],
                        "name": c.get("name"),
                        "execution_count": len(execs),
                    }
                )
        else:
            for c in cycles:
                execs = client.list_executions_in_cycle(c["key"])
                keys = [k for k in (test_case_key_from_execution(e) for e in execs) if k]
                exec_total += len(keys)
                cycle_details.append(
                    {
                        "source_key": c["key"],
                        "name": c.get("name"),
                        "execution_count": len(keys),
                        "test_case_keys": keys,
                    }
                )
            plan["cycles"].extend(
                {
                    "source_folder_id": folder.id,
                    "source_folder_name": folder.name,
                    **cd,
                }
                for cd in cycle_details
            )
            plan["execution_count"] += exec_total
        plan["folders"].append(
            {
                "source_id": folder.id,
                "name": folder.name,
                "parent_source_id": folder.parent_id,
                "cycle_count": len(cycles),
                "cycles_to_clone": 0 if skip else len(cycles),
                "cycles_skipped": skip,
                "execution_count": exec_total,
            }
        )
    return plan


def execute_clone(
    client: ZephyrClient,
    *,
    source_root: FolderNode,
    new_root_name: str,
    dry_run: bool,
    skip_cycle_folder_names: set[str],
    ignore_case: bool,
) -> dict[str, Any]:
    folder_order = walk_folders_bfs(source_root)
    id_map: dict[int, int] = {}
    results: dict[str, Any] = {
        "dry_run": dry_run,
        "new_root_name": new_root_name,
        "skip_cycle_folder_names": sorted(skip_cycle_folder_names),
        "folders_created": [],
        "cycles_created": [],
        "cycles_skipped": [],
        "executions_created": 0,
        "errors": [],
    }

    for folder in folder_order:
        if folder.id == source_root.id:
            parent_id = source_root.parent_id
            folder_name = new_root_name
        else:
            parent_id = id_map.get(folder.parent_id)  # type: ignore[arg-type]
            folder_name = folder.name

        folder_body = {
            "projectKey": client.project_key,
            "name": folder_name,
            "folderType": "TEST_CYCLE",
        }
        if parent_id is not None:
            folder_body["parentId"] = parent_id

        if dry_run:
            new_folder_id = -(folder.id)
            print(f"[dry-run] POST /folders  name={folder_name!r} parentId={parent_id}")
        else:
            status, data = client.request("POST", "/folders", body=folder_body)
            if status not in (200, 201):
                msg = f"Create folder {folder_name!r} failed HTTP {status}: {data}"
                results["errors"].append(msg)
                raise RuntimeError(msg)
            new_folder_id = int(data["id"])
            print(f"Created folder {folder_name!r} id={new_folder_id} (from source {folder.id})")

        id_map[folder.id] = new_folder_id
        results["folders_created"].append(
            {"name": folder_name, "source_id": folder.id, "new_id": new_folder_id}
        )

        if should_skip_cycles(folder.name, skip_cycle_folder_names, ignore_case=ignore_case):
            cycles = client.list_cycles_in_folder(folder.id)
            print(
                f"Skipping {len(cycles)} cycle(s) in folder {folder_name!r} "
                f"(folder created; cycles not cloned)"
            )
            for cycle in cycles:
                results["cycles_skipped"].append(
                    {
                        "folder_name": folder_name,
                        "source_key": cycle["key"],
                        "name": cycle.get("name"),
                    }
                )
            continue

        cycles = client.list_cycles_in_folder(folder.id)
        for cycle in cycles:
            cycle_body: dict[str, Any] = {
                "projectKey": client.project_key,
                "name": cycle.get("name"),
                "folderId": new_folder_id,
                "statusName": "Not Executed",
            }
            for field in ("description", "plannedStartDate", "plannedEndDate"):
                if cycle.get(field):
                    cycle_body[field] = cycle[field]

            if dry_run:
                new_cycle_key = f"DRY-R-{cycle['key']}"
                print(
                    f"[dry-run] POST /testcycles name={cycle.get('name')!r} "
                    f"folderId={new_folder_id} executions=..."
                )
            else:
                status, data = client.request("POST", "/testcycles", body=cycle_body)
                if status not in (200, 201):
                    msg = f"Create cycle {cycle.get('name')!r} failed HTTP {status}: {data}"
                    results["errors"].append(msg)
                    raise RuntimeError(msg)
                new_cycle_key = data.get("key") or data.get("id")
                print(f"Created cycle {new_cycle_key} {cycle.get('name')!r}")

            execs = client.list_executions_in_cycle(cycle["key"])
            created_execs = 0
            for ex in execs:
                tc_key = test_case_key_from_execution(ex)
                if not tc_key:
                    results["errors"].append(
                        f"Skip execution in {cycle['key']}: no test case key"
                    )
                    continue
                exec_body = {
                    "projectKey": client.project_key,
                    "testCaseKey": tc_key,
                    "testCycleKey": new_cycle_key,
                    "statusName": "Not Executed",
                }
                if dry_run:
                    created_execs += 1
                else:
                    status, data = client.request("POST", "/testexecutions", body=exec_body)
                    if status not in (200, 201):
                        msg = (
                            f"Create execution {tc_key} in {new_cycle_key} "
                            f"failed HTTP {status}: {data}"
                        )
                        results["errors"].append(msg)
                        print(f"WARN: {msg}", file=sys.stderr)
                        continue
                    created_execs += 1
                    time.sleep(0.05)

            results["executions_created"] += created_execs
            results["cycles_created"].append(
                {
                    "source_key": cycle["key"],
                    "new_key": new_cycle_key,
                    "name": cycle.get("name"),
                    "executions": created_execs,
                    "folder_id": new_folder_id,
                }
            )

    return results


def main() -> int:
    load_dotenv()
    p = argparse.ArgumentParser(
        description="Clone a Zephyr Scale TEST_CYCLE folder tree (subfolders + cycles + assignments)."
    )
    p.add_argument(
        "--source-folder-name",
        required=True,
        help="Exact name of the existing test-cycle folder to clone",
    )
    p.add_argument(
        "--new-folder-name",
        required=True,
        help="Name for the new root folder (clone destination)",
    )
    p.add_argument("--project-key", default=os.environ.get("ZEPHYR_PROJECT_KEY"))
    p.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive folder name match",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan and simulate creates without POST",
    )
    p.add_argument(
        "--plan-only",
        action="store_true",
        help="Only print inventory (folders/cycles/executions); no creates",
    )
    p.add_argument(
        "--skip-cycle-folders",
        nargs="*",
        metavar="NAME",
        help=(
            "Subfolder names whose test cycles are not cloned (folder still created). "
            "Default: Automation. Pass with no values to skip none."
        ),
    )
    p.add_argument(
        "--include-automation-cycles",
        action="store_true",
        help="Clone test cycles inside the Automation subfolder (overrides default skip)",
    )
    args = p.parse_args()

    skip_cycle_folder_names = resolve_skip_cycle_folder_names(
        args.skip_cycle_folders,
        include_automation_cycles=args.include_automation_cycles,
    )

    token = os.environ.get("ZEPHYR_ACCESS_TOKEN") or os.environ.get("ZEPHYR_SCALE_TOKEN")
    if not token:
        print("Missing ZEPHYR_ACCESS_TOKEN", file=sys.stderr)
        return 2
    if not args.project_key:
        print("Missing ZEPHYR_PROJECT_KEY or --project-key", file=sys.stderr)
        return 2

    base = os.environ.get(
        "ZEPHYR_CLOUD_BASE_URL", "https://api.zephyrscale.smartbear.com/v2"
    )
    client = ZephyrClient(base, token, args.project_key)

    if not args.dry_run and not args.plan_only:
        status, _ = client.request(
            "GET",
            "/testcases",
            params={
                "projectKey": args.project_key,
                "maxResults": "1",
                "startAt": "0",
            },
        )
        if status != 200:
            print(f"Zephyr auth check failed HTTP {status}", file=sys.stderr)
            return 1

    all_folders = client.list_test_cycle_folders()
    matches = find_folders_by_name(
        all_folders, args.source_folder_name, ignore_case=args.ignore_case
    )
    if not matches:
        print(
            f"No TEST_CYCLE folder named {args.source_folder_name!r} in {args.project_key}",
            file=sys.stderr,
        )
        return 1
    if len(matches) > 1:
        print(
            f"Multiple folders match {args.source_folder_name!r}; use folder id instead:",
            file=sys.stderr,
        )
        for m in matches:
            print(f"  id={m['id']} parentId={m.get('parentId')}", file=sys.stderr)
        return 1

    source_raw = matches[0]
    source_id = int(source_raw["id"])
    new_matches = find_folders_by_name(
        all_folders, args.new_folder_name, ignore_case=args.ignore_case
    )
    if new_matches:
        print(
            f"Folder {args.new_folder_name!r} already exists (id={new_matches[0]['id']}). "
            "Choose a different --new-folder-name.",
            file=sys.stderr,
        )
        return 1

    subtree = build_subtree(all_folders, source_id)
    print(f"Source: {args.source_folder_name!r} (id={source_id})")
    print(f"New root: {args.new_folder_name!r}")
    print(f"Subfolders in tree: {len(walk_folders_bfs(subtree)) - 1}")
    if skip_cycle_folder_names:
        print(f"Skip test cycles in folders: {', '.join(sorted(skip_cycle_folder_names))}")

    plan = plan_clone(
        client,
        subtree,
        skip_cycle_folder_names=skip_cycle_folder_names,
        ignore_case=args.ignore_case,
    )
    skipped_count = len(plan["cycles_skipped"])
    print(
        f"Plan: {len(plan['folders'])} folder(s), {len(plan['cycles'])} cycle(s) to clone, "
        f"{skipped_count} cycle(s) skipped, "
        f"{plan['execution_count']} test case assignment(s)"
    )

    if args.plan_only:
        print(json.dumps(plan, indent=2)[:12000])
        return 0

    results = execute_clone(
        client,
        source_root=subtree,
        new_root_name=args.new_folder_name,
        dry_run=args.dry_run,
        skip_cycle_folder_names=skip_cycle_folder_names,
        ignore_case=args.ignore_case,
    )
    print("\n--- Summary ---")
    print(json.dumps(results, indent=2))
    return 0 if not results.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())

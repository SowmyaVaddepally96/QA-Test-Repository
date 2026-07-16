---
name: zephyr-clone-test-cycle-folder
description: >-
  Clones a Zephyr Scale TEST_CYCLE folder tree (subfolders, test cycles, and test
  case assignments) via REST on Jira Cloud. User supplies source folder name and
  new folder name. Use when the user asks to clone, copy, or duplicate test cycle
  folders in Zephyr Scale, TM4J, or regression folder structures for a new release.
---

# Zephyr Scale — clone test cycle folder

## Purpose

Duplicate an existing **Test Cycles** folder in **Zephyr Scale Cloud**, including:

- **All subfolders** (preserved names and hierarchy under a new root)
- **All test cycles** in each folder **except** subfolders named **`Automation`** (see below)
- **All test cases assigned** to each cloned cycle (via `POST /testexecutions`; status **Not Executed**)

### Automation folder (default skip)

The subfolder **`Automation`** is **always created** under the new root, but its **test cycles are not cloned** (automation runs are environment-specific). To clone Automation cycles too, pass **`--include-automation-cycles`** on the script.

There is **no native clone API** ([SmartBear community](https://community.smartbear.com/discussions/zephyrscale/zephyr-scale-ability-to-clone-test-cycle-folders/257322)); this skill uses the bundled script to recreate structure with REST calls.

## Prerequisites

1. **Zephyr Scale Cloud** (not Squad). Auth: [../zephyr-scale/SKILL.md](../zephyr-scale/SKILL.md) — `ZEPHYR_ACCESS_TOKEN`, `ZEPHYR_PROJECT_KEY`, optional `ZEPHYR_CLOUD_BASE_URL`.
2. Run `python .cursor/skills/zephyr-scale/scripts/zephyr_request.py ping` before live clones.
3. User must have Scale permissions to create folders, cycles, and executions in the project.

## Required inputs (ask before live run)

| Input | Flag | Notes |
|-------|------|--------|
| **Source folder name** | `--source-folder-name` | Exact name of the folder to clone (TEST_CYCLE type). |
| **New folder name** | `--new-folder-name` | Name for the **new root** folder. Must **not** already exist. |

Optional: `--project-key` (defaults to `ZEPHYR_PROJECT_KEY`), `--ignore-case` for name matching.

**Cycle skip (default):** subfolder **`Automation`** — folder created, cycles skipped. Override with `--include-automation-cycles`. Add other skip names with `--skip-cycle-folders NAME …`; pass `--skip-cycle-folders` alone to skip none.

**Do not** ask for numeric folder ids unless name lookup fails or multiple matches exist.

## Agent workflow

1. **Collect** source folder name and new folder name from the user (both required).
2. **Plan first:** run with `--plan-only` to show folder/cycle/execution counts.
3. **Dry-run:** run with `--dry-run` and show output; confirm with user before live POST.
4. **Live clone:** run without `--dry-run` only after explicit approval.
5. **Summarize:** new root folder name, folder/cycle/execution counts, any warnings.

## Script

From repo root:

```bash
# Inventory only
python .cursor/skills/zephyr-clone-test-cycle-folder/scripts/clone_test_cycle_folder.py \
  --source-folder-name "Regression 2026MAR17" \
  --new-folder-name "Regression 2026MAY28" \
  --plan-only

# Dry-run (no POST)
python .cursor/skills/zephyr-clone-test-cycle-folder/scripts/clone_test_cycle_folder.py \
  --source-folder-name "Regression 2026MAR17" \
  --new-folder-name "Regression 2026MAY28" \
  --dry-run

# Live clone
python .cursor/skills/zephyr-clone-test-cycle-folder/scripts/clone_test_cycle_folder.py \
  --source-folder-name "Regression 2026MAR17" \
  --new-folder-name "Regression 2026MAY28"
```

## Behavior notes

- New root folder is a **sibling** of the source (same `parentId` as source root).
- Subfolder **names** are unchanged under the new root.
- Subfolder **`Automation`**: folder is created; **test cycles inside it are not cloned** (default). Use `--include-automation-cycles` to copy them.
- Cycle **metadata** copied when present: `description`, `plannedStartDate`, `plannedEndDate`.
- Execution **results** are **not** copied — assignments only, status **Not Executed**.
- **Issue links** on cycles are not copied (API limitation for this script).
- Re-running with the same `--new-folder-name` fails if that folder already exists.
- Large trees: script paginates API calls; may take several minutes; handles HTTP 429 with retry.

## Troubleshooting

| Symptom | Action |
|---------|--------|
| Folder name not found | List folders via GET `/folders?folderType=TEST_CYCLE`; check spelling/case or use `--ignore-case`. |
| Multiple matches | Ask user which folder id to use; extend script with `--source-folder-id` if needed. |
| New name exists | Pick a different `--new-folder-name`. |
| 401 on POST | Refresh `ZEPHYR_ACCESS_TOKEN` in Jira → Zephyr Scale → API tokens. |
| Execution POST fails | Test case may be archived/deleted; note warning and continue. |

## Additional resources

- API endpoints and limits: [reference.md](reference.md)
- General Scale auth: [../zephyr-scale/SKILL.md](../zephyr-scale/SKILL.md)

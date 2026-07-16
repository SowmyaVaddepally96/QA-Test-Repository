Use the agent defined in:
.cursor/agents/zephyr-clone-test-cycle-folder.md

Follow:
.cursor/skills/zephyr-clone-test-cycle-folder/SKILL.md

Auth and REST details:
.cursor/skills/zephyr-scale/SKILL.md

TASK:
Clone a **Zephyr Scale Test Cycles folder** (including **all subfolders**, **test cycles**, and **test case assignments**) into a **new folder** with the name the user provides.

**Default:** subfolder **`Automation`** is created but its **test cycles are not cloned**. Mention this in plan/dry-run summaries.

INPUT (collect both before any live POST):
- **Source folder name** — existing Test Cycles folder to copy from
- **New folder name** — name for the new root folder (must not already exist)

WORKFLOW:
1. Run `--plan-only` and report folder / cycle / assignment counts.
2. Run `--dry-run` unless the user explicitly skips after seeing the plan.
3. Run **live clone** only after explicit user approval.

SCRIPT:
.cursor/skills/zephyr-clone-test-cycle-folder/scripts/clone_test_cycle_folder.py

INPUT:
{{input}}

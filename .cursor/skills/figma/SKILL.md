---
name: figma
description: Use this skill when the user wants to extract design structure from Figma files for test case generation. Triggers on Figma URLs, file keys, or requests to generate tests from designs. Focuses on functionality — interactions, navigation flows, component states, variables, and behavioral specs — not appearance (colors, typography, effects). Requires a Figma Personal Access Token.
---

# Figma Design Extraction for Test Case Generation

## Overview

This skill fetches Figma design data via the REST API and maps it to test cases. The focus is on **functional behavior** — what users can do, what states exist, and how screens connect — not visual appearance.

## Setup

The Figma REST API requires a Personal Access Token (PAT).

**Provide the token via a `.env` file (recommended):**

Place a `.env` file in the figma skill directory (e.g. `.cursor/skills/figma/.env`) with:

```
FIGMA_TOKEN=figd_...
```

The script automatically loads `FIGMA_TOKEN` and `FIGMA_PASSWORD` from the first `.env` it finds in: the skill directory, the script directory, or the current working directory. Environment variables already set take precedence. For **downloading and storing data locally**, use the direct API script (`figma_download.py`) so only the token is used—no password flow or rate-limited endpoints.

**Or set the token in the environment:**
```bash
export FIGMA_TOKEN="figd_..."
```

**Download from URL:** You can pass a full Figma URL as `--file-key`. The file key and optional `node-id` (e.g. `?node-id=8062-9900`) are parsed from the URL; no need to pass `--node-ids` separately when the URL includes a node.

**Password-protected files:** Figma's link-sharing password gate is enforced server-side and blocks even authenticated API requests (returning 403). To access password-protected files, provide the password via `--password` flag or `FIGMA_PASSWORD` environment variable:
```bash
# Via flag
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz --password SECRET

# Via environment variable
export FIGMA_PASSWORD="SECRET"
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz
```
This uses Figma's browser-internal `check_password` endpoint to unlock access before making API calls. The `--password` flag takes precedence over the environment variable.

### Getting a File Key and Node from URL

You can pass a full Figma URL as `--file-key`; the script extracts the file key and, if present, the node ID:

- File key: the segment after `/design/` or `/file/` (e.g. `ABC123xyz`).
- Node ID: from `node-id=8062-9900` in the query string → used as `--node-ids 8062:9900` automatically.

Example: `https://www.figma.com/design/yFFgIDlTbDcQAbICJyFEuu/Sophi---Developers-Hand-Off?node-id=8062-9900` downloads that file scoped to node `8062:9900`.

## Workflow

Based on what the user needs, choose the appropriate extraction:

1. **"Download this Figma file" / "Save the board locally"** → Use **direct API download** (recommended) to fetch via the API with your token only and store locally. This bypasses the password/rate-limited script. Use the full script's `download` only for password-protected files.
2. **"Generate test cases from this Figma file"** → Start with `full` to get a complete picture
3. **"What screens/pages exist?"** → Use `structure` to get the page and frame hierarchy
4. **"What interactions/flows are defined?"** → Use `interactions` to get triggers, actions, and navigation
5. **"What component states exist?"** → Use `components` to get variants and properties
6. **"What variables/conditions are used?"** → Use `variables` to get boolean flags, string tokens, and modes
7. **"Are there any design comments/specs?"** → Use `comments` to get behavioral annotations

## Direct API Download (recommended for "download and store locally")

For **downloading Figma data and storing it locally**, use the **direct API** path. This uses a single authenticated GET to the Figma REST API (token only)—no password flow, no rate-limited browser endpoints.

**Script:** `scripts/figma_download.py` — minimal script that only calls `GET /v1/files/:key` and saves the JSON.

```bash
# From repo root; output defaults to <fileName>_<fileKey>.json in current directory
python .cursor/skills/figma/scripts/figma_download.py "https://www.figma.com/design/ABC123xyz/My-Project"

# Save to a specific path
python .cursor/skills/figma/scripts/figma_download.py ABC123xyz -o figma_output.json

# Save into a directory (creates dir if needed)
python .cursor/skills/figma/scripts/figma_download.py ABC123xyz --output-dir ./figma_data

# Optional: limit depth or scope to nodes
python .cursor/skills/figma/scripts/figma_download.py ABC123xyz --depth 5
```

Output is stored **locally** (path you pass with `-o` or `--output-dir`, or CWD). Use this for archival, offline analysis, or as the source for test-case extraction. For **password-protected** files, use the full script with `--password` (see below); that path is rate-limited.

## Using the Full Script (structure, interactions, password-protected)

The script at `.cursor/skills/figma/scripts/figma_fetch.py` wraps the Figma REST API and adds structure/interactions/components extraction and optional password unlock.

### Download via full script (when you need password unlock)

If the file is **password-protected**, use the full script's `download` subcommand with `--password` or `FIGMA_PASSWORD` (this uses a rate-limited browser endpoint to unlock first):

```bash
python .cursor/skills/figma/scripts/figma_fetch.py download --file-key ABC123xyz --password SECRET -o figma_output.json
```

For non–password-protected files, prefer `figma_download.py` above.

### Extracting for Test Cases

```bash
# Get full overview (all data combined)
python .cursor/skills/figma/scripts/figma_fetch.py full --file-key ABC123xyz

# Or pass a full Figma URL (file key is extracted automatically)
python .cursor/skills/figma/scripts/figma_fetch.py full --file-key "https://www.figma.com/design/ABC123xyz/My-Project"

# Fetch only structure (pages and frames)
python .cursor/skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz

# Fetch interactions and flows
python .cursor/skills/figma/scripts/figma_fetch.py interactions --file-key ABC123xyz

# Fetch component metadata
python .cursor/skills/figma/scripts/figma_fetch.py components --file-key ABC123xyz

# Fetch variables
python .cursor/skills/figma/scripts/figma_fetch.py variables --file-key ABC123xyz

# Fetch comments
python .cursor/skills/figma/scripts/figma_fetch.py comments --file-key ABC123xyz

# Write any output to a local file (-o / --output)
python .cursor/skills/figma/scripts/figma_fetch.py full --file-key ABC123xyz -o figma_full.json

# Scope to specific node IDs
python .cursor/skills/figma/scripts/figma_fetch.py interactions --file-key ABC123xyz --node-ids "1:2,3:4"

# Control structure depth (default: 3)
python .cursor/skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz --depth 2
```

## Interpreting Results for Test Cases

Map Figma concepts to test cases as follows:

### Screens/Pages → Test Scenarios
Each top-level frame in a page typically represents a screen or state. Use these as the basis for test scenarios.

### Interactions (Triggers + Actions) → User Action Test Cases
Each interaction defines a user action and its expected outcome:
- **Trigger** (ON_CLICK, ON_HOVER, ON_DRAG, AFTER_TIMEOUT, etc.) → the user action to perform
- **Action** (NAVIGATE, SWAP_OVERLAY, OPEN_URL, SET_VARIABLE, etc.) → the expected result
- **Transition destination** → the screen the user should land on

### Flow Starting Points → User Journey Entry Points
Figma's prototype flow starting points define where user journeys begin. Each is a named entry point for an end-to-end test.

### Component Variants/Properties → State-Based Test Cases
Component properties define the states a UI element can be in:
- **VARIANT** properties → distinct visual/functional states (e.g., "State: Default, Hover, Disabled")
- **BOOLEAN** properties → toggle states (e.g., "Show Icon: true/false")
- **TEXT** properties → content variations
- **INSTANCE_SWAP** properties → slot-based composition variations

Generate test cases for each meaningful combination of property values.

### Variables → Conditional Behavior Tests
Figma variables represent dynamic values that drive conditional logic:
- **BOOLEAN** variables → feature flags, visibility toggles
- **STRING** variables → text content that changes per mode/context
- **Variable modes** → different contexts (e.g., "Light/Dark", "English/French", "Logged In/Logged Out")

### Comments → Requirements and Acceptance Criteria
Design comments often contain behavioral specifications, edge cases, and acceptance criteria. Review these for test requirements that may not be captured in the visual design.

## Reference

For detailed Figma API endpoints, node types, and data model documentation, see `reference.md` in this skill directory.

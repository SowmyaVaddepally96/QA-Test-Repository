---
name: figma
description: Use this skill when the user wants to extract design structure from Figma files for test case generation. Triggers on Figma URLs, file keys, or requests to generate tests from designs. Focuses on functionality — interactions, navigation flows, component states, variables, and behavioral specs — not appearance (colors, typography, effects). Requires a Figma Personal Access Token.
---

# Figma Design Extraction for Test Case Generation

## Overview

This skill fetches Figma design data via the REST API and maps it to test cases. The focus is on **functional behavior** — what users can do, what states exist, and how screens connect — not visual appearance.

## Setup

The Figma REST API requires a Personal Access Token (PAT).

**Provide the token via environment variable:**
```bash
export FIGMA_TOKEN="figd_..."
```

**Password-protected files:** Figma's link-sharing password gate is enforced server-side and blocks even authenticated API requests (returning 403). To access password-protected files, provide the password via `--password` flag or `FIGMA_PASSWORD` environment variable:
```bash
# Via flag
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz --password SECRET

# Via environment variable
export FIGMA_PASSWORD="SECRET"
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz
```
This uses Figma's browser-internal `check_password` endpoint to unlock access before making API calls. The `--password` flag takes precedence over the environment variable.

### Getting a File Key

From any Figma URL, the file key is the segment after `/design/` or `/file/`:
```
https://www.figma.com/design/ABC123xyz/My-Project → file key: ABC123xyz
https://www.figma.com/file/ABC123xyz/My-Project   → file key: ABC123xyz
```

## Workflow

Based on what the user needs, choose the appropriate extraction:

1. **"Generate test cases from this Figma file"** → Start with `full` to get a complete picture
2. **"What screens/pages exist?"** → Use `structure` to get the page and frame hierarchy
3. **"What interactions/flows are defined?"** → Use `interactions` to get triggers, actions, and navigation
4. **"What component states exist?"** → Use `components` to get variants and properties
5. **"What variables/conditions are used?"** → Use `variables` to get boolean flags, string tokens, and modes
6. **"Are there any design comments/specs?"** → Use `comments` to get behavioral annotations

## Using the Script

The bundled script at `skills/figma/scripts/figma_fetch.py` wraps the Figma REST API.

```bash
# Get full overview (all data combined)
python skills/figma/scripts/figma_fetch.py full --file-key ABC123xyz

# Or pass a full Figma URL (file key is extracted automatically)
python skills/figma/scripts/figma_fetch.py full --file-key "https://www.figma.com/design/ABC123xyz/My-Project"

# Fetch only structure (pages and frames)
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz

# Fetch interactions and flows
python skills/figma/scripts/figma_fetch.py interactions --file-key ABC123xyz

# Fetch component metadata
python skills/figma/scripts/figma_fetch.py components --file-key ABC123xyz

# Fetch variables
python skills/figma/scripts/figma_fetch.py variables --file-key ABC123xyz

# Fetch comments
python skills/figma/scripts/figma_fetch.py comments --file-key ABC123xyz

# Scope to specific node IDs
python skills/figma/scripts/figma_fetch.py interactions --file-key ABC123xyz --node-ids "1:2,3:4"

# Control structure depth (default: 3)
python skills/figma/scripts/figma_fetch.py structure --file-key ABC123xyz --depth 2
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

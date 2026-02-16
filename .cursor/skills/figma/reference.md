# Figma API & Data Model Reference

Concise reference for the Figma REST API endpoints and data structures relevant to test case generation.

## Extracting a File Key from a URL

```
https://www.figma.com/design/<FILE_KEY>/<title>?node-id=<NODE_ID>
https://www.figma.com/file/<FILE_KEY>/<title>
```

The file key is the path segment immediately after `/design/` or `/file/`. Node IDs in the URL use `-` as separator (e.g., `1-2`) but the API uses `:` (e.g., `1:2`).

## API Endpoints

All endpoints require the `X-Figma-Token` header with a Personal Access Token.

### 1. GET /v1/files/:file_key

Returns the full document tree.

| Parameter | Description |
|-----------|-------------|
| `depth`   | Positive integer. Limits tree traversal depth. |
| `ids`     | Comma-separated node IDs. Returns only those subtrees. |
| `geometry` | Set to `paths` to include vector path data. Usually not needed. |

**Response keys (functional):** `name`, `lastModified`, `version`, `document`, `components`, `componentSets`, `schemaVersion`

### 2. GET /v1/files/:file_key/nodes

Returns specific nodes by ID with full subtree.

| Parameter | Description |
|-----------|-------------|
| `ids`     | Comma-separated node IDs (required). |
| `depth`   | Limits subtree depth per node. |

### 3. GET /v1/files/:file_key/comments

Returns all comments on a file.

**Response:** Array of comment objects with `id`, `message`, `created_at`, `resolved_at`, `user`, `client_meta` (position), `parent_id` (for replies), `order_id`.

### 4. GET /v1/files/:file_key/variables/local

Returns local variables and variable collections defined in the file.

**Response structure:**
```
meta.variables.<id>: { name, resolvedType, valuesByMode, scopes, ... }
meta.variableCollections.<id>: { name, modes, defaultModeId, ... }
```

### 5. GET /v1/files/:file_key/component_sets

Returns published component set metadata. Less detailed than the file endpoint for local components.

## Node Types (Functional Properties Only)

| Type | Key Functional Properties |
|------|--------------------------|
| DOCUMENT | `children` (pages) |
| CANVAS (page) | `children` (top-level frames), `flowStartingPoints` |
| FRAME | `children`, `name`, `interactions`, `flowStartingPoints`, `componentProperties` |
| GROUP | `children`, `name` |
| COMPONENT | `children`, `name`, `componentProperties`, `interactions` |
| COMPONENT_SET | `children` (variant components), `name`, `componentProperties` |
| INSTANCE | `children`, `name`, `componentId`, `componentProperties`, `interactions` |
| TEXT | `name`, `characters` (the text content) |
| VECTOR | `name`, `interactions` |
| BOOLEAN_OPERATION | `children`, `booleanOperation` |
| SECTION | `children`, `name` |

## Interaction Model

Interactions are defined on nodes as an `interactions` array. Each interaction has:

### Triggers

| Type | Description |
|------|-------------|
| ON_CLICK | User clicks/taps the element |
| ON_HOVER | User hovers over the element |
| ON_PRESS | User presses and holds |
| ON_DRAG | User drags the element |
| AFTER_TIMEOUT | Fires after a delay (ms) |
| MOUSE_ENTER | Mouse enters the element bounds |
| MOUSE_LEAVE | Mouse leaves the element bounds |
| MOUSE_DOWN | Mouse button pressed |
| MOUSE_UP | Mouse button released |
| ON_KEY_DOWN | Keyboard key pressed |

### Actions

| Type | Description | Key Fields |
|------|-------------|------------|
| NAVIGATE | Navigate to a frame | `destinationId`, `navigationType` |
| SWAP_OVERLAY | Replace current overlay | `destinationId`, `overlayRelativePosition` |
| OPEN_OVERLAY | Open as overlay | `destinationId`, `overlayRelativePosition` |
| CLOSE_OVERLAY | Close the current overlay | — |
| BACK | Navigate back in prototype | — |
| OPEN_URL | Open an external URL | `url` |
| SET_VARIABLE | Set a variable value | `variableId`, `variableValue` |
| CONDITIONAL | Branch based on variable | `conditionalActions` |

### Navigation Types (for NAVIGATE action)

| Type | Description |
|------|-------------|
| NAVIGATE | Standard forward navigation |
| SWAP | Replace current screen |
| OVERLAY | Open as overlay on top |
| SCROLL_TO | Scroll to a position |
| CHANGE_TO | Change component variant |

## Component Properties

Components and component sets expose `componentProperties`:

| Property Type | Description | Test Relevance |
|---------------|-------------|----------------|
| VARIANT | Enum of variant values | Each value is a distinct state to test |
| BOOLEAN | true/false toggle | Two states: shown/hidden, enabled/disabled |
| TEXT | Overridable text content | Content variations to test |
| INSTANCE_SWAP | Swappable nested instance | Different sub-component configurations |

**Variant naming convention:** Figma encodes variants as `Property1=Value1, Property2=Value2` in the component name.

## Variable Types

| resolvedType | Description | Test Relevance |
|--------------|-------------|----------------|
| BOOLEAN | true/false | Feature flags, visibility toggles |
| FLOAT | Numeric value | Thresholds, counts, dimensions |
| STRING | Text value | Labels, content tokens |
| COLOR | Color value | (Usually appearance — skip for functional tests) |

### Variable Modes

Variables are organized in **collections**, each with one or more **modes**. Modes represent different contexts:
- Light / Dark (theme)
- English / French / Spanish (locale)
- Logged In / Logged Out (auth state)
- Desktop / Mobile (breakpoint)

Each variable has `valuesByMode` mapping mode IDs to values. The collection's `modes` array maps mode IDs to human-readable names.

## Password-Protected Files

Figma's link-sharing password gate is enforced server-side and returns 403 on API requests, even with a valid PAT. The only workaround is Figma's undocumented browser endpoint:

### POST https://www.figma.com/api/files/:file_key/check_password

Unlocks a password-protected file by setting a session cookie.

| Detail | Value |
|--------|-------|
| Content-Type | `application/json` |
| Body | `{"password": "..."}` |
| Success | 200 — sets a session cookie granting access |
| Failure | Non-200 — password rejected |

The session cookie must be included in subsequent API requests alongside the `X-Figma-Token` header. This is an undocumented endpoint (used by Figma's own browser client) and may change without notice.

## Tips for Token-Efficient Fetching

1. **Use `depth` parameter** to limit tree traversal — depth 2-3 is usually sufficient for structure
2. **Use `ids` parameter** to fetch only relevant sections instead of the full file
3. **Large files:** Fetch structure first at shallow depth, identify relevant node IDs, then fetch details for those nodes only
4. **Variables endpoint** is lightweight — always safe to call
5. **Comments endpoint** is lightweight — always safe to call

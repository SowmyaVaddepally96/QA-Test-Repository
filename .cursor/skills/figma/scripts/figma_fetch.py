#!/usr/bin/env python3
"""
Figma REST API wrapper for extracting design structure focused on functionality.

Fetches Figma file data and outputs functionality-focused JSON, stripping
appearance-only properties (fills, strokes, colors, effects, text styles).

Usage:
    python figma_fetch.py <subcommand> --file-key <KEY_OR_URL> [options]

Subcommands:
    structure     Fetch page/frame hierarchy at controlled depth
    interactions  Extract interactions, triggers, actions, and flow starting points
    components    Fetch component metadata (variants, properties, states)
    variables     Fetch local variables (booleans, strings, modes)
    comments      Fetch file comments
    full          Run all of the above combined

Requires FIGMA_TOKEN environment variable to be set to a Personal Access Token.
"""

import argparse
import http.cookiejar
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse


BASE_URL = "https://api.figma.com/v1"

# Properties to strip from nodes (appearance-only, not functional)
APPEARANCE_KEYS = frozenset({
    "fills", "strokes", "strokeWeight", "strokeAlign", "strokeCap",
    "strokeJoin", "strokeDashes", "dashPattern",
    "effects", "blendMode", "opacity", "isMask",
    "backgroundColor", "backgroundColorHex",
    "cornerRadius", "rectangleCornerRadii",
    "style", "styles", "fontFamily", "fontWeight", "fontSize",
    "letterSpacing", "lineHeightPx", "lineHeightPercent",
    "lineHeightPercentFontSize", "lineHeightUnit",
    "textAlignHorizontal", "textAlignVertical", "textAutoResize",
    "textDecoration", "textCase",
    "fillGeometry", "strokeGeometry",
    "arcData", "constraints", "layoutAlign", "layoutGrow",
    "layoutPositioning", "layoutSizingHorizontal", "layoutSizingVertical",
    "primaryAxisSizingMode", "counterAxisSizingMode",
    "primaryAxisAlignItems", "counterAxisAlignItems",
    "paddingLeft", "paddingRight", "paddingTop", "paddingBottom",
    "itemSpacing", "counterAxisSpacing",
    "absoluteBoundingBox", "absoluteRenderBounds", "relativeTransform",
    "size", "minWidth", "maxWidth", "minHeight", "maxHeight",
    "exportSettings", "preserveRatio",
})


def extract_file_key(key_or_url):
    """Extract file key from a Figma URL or return as-is if already a key."""
    # Match Figma URLs: /design/KEY/... or /file/KEY/...
    match = re.search(r'figma\.com/(?:design|file)/([a-zA-Z0-9]+)', key_or_url)
    if match:
        return match.group(1)
    # If no URL pattern matched, treat as raw key
    return key_or_url.strip()


def build_opener():
    """Build a urllib opener with cookie support for password-protected files."""
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def unlock_file(file_key, password, opener):
    """Unlock a password-protected Figma file using the browser check_password endpoint.

    This POSTs to Figma's undocumented (browser-internal) endpoint to set a session
    cookie that grants access. The cookie is captured by the opener's cookie jar and
    included in all subsequent requests.
    """
    url = f"https://www.figma.com/api/files/{file_key}/check_password"
    body = json.dumps({"password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with opener.open(req) as resp:
            if resp.status >= 300:
                print(f"Error: Password rejected (HTTP {resp.status})", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"Error: Password check failed (HTTP {e.code}): {body_text}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Figma for password check: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_request(endpoint, token, params=None, opener=None):
    """Make an authenticated GET request to the Figma API."""
    url = f"{BASE_URL}{endpoint}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    req = urllib.request.Request(url)
    req.add_header("X-Figma-Token", token)

    try:
        if opener:
            resp = opener.open(req)
        else:
            resp = urllib.request.urlopen(req)
        with resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Figma API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Figma API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def strip_appearance(node):
    """Remove appearance-only properties from a node, keeping functional data."""
    return {k: v for k, v in node.items() if k not in APPEARANCE_KEYS}


def clean_node(node, depth=None, current_depth=0):
    """Recursively clean a node tree: strip appearance, respect depth limit."""
    cleaned = strip_appearance(node)

    # Recursively clean children
    if "children" in cleaned:
        if depth is not None and current_depth >= depth:
            child_count = len(cleaned["children"])
            del cleaned["children"]
            cleaned["_childCount"] = child_count
        else:
            cleaned["children"] = [
                clean_node(child, depth, current_depth + 1)
                for child in cleaned["children"]
            ]

    return cleaned


def extract_interactions_from_node(node, path=""):
    """Recursively extract interactions from a node tree."""
    results = []
    node_name = node.get("name", "")
    node_id = node.get("id", "")
    current_path = f"{path}/{node_name}" if path else node_name

    # Extract interactions (prototype connections)
    interactions = node.get("interactions", [])
    if interactions:
        for interaction in interactions:
            trigger = interaction.get("trigger", {})
            actions = interaction.get("actions", [])
            for action in actions:
                results.append({
                    "nodeId": node_id,
                    "nodeName": node_name,
                    "path": current_path,
                    "trigger": {
                        "type": trigger.get("type"),
                    },
                    "action": {
                        "type": action.get("type"),
                        "navigationType": action.get("navigationType"),
                        "destinationId": action.get("destinationId"),
                        "url": action.get("url"),
                        "overlay": {
                            "position": action.get("overlayRelativePosition"),
                        } if action.get("type") in ("OPEN_OVERLAY", "SWAP_OVERLAY") else None,
                    },
                    "transition": {
                        "type": action.get("transition", {}).get("type") if action.get("transition") else None,
                        "duration": action.get("transition", {}).get("duration") if action.get("transition") else None,
                    } if action.get("transition") else None,
                })

    # Extract from children
    for child in node.get("children", []):
        results.extend(extract_interactions_from_node(child, current_path))

    return results


def extract_flow_starting_points(document):
    """Extract prototype flow starting points from the document."""
    flows = []
    for page in document.get("children", []):
        page_name = page.get("name", "")
        for child in page.get("children", []):
            starting_points = child.get("flowStartingPoints", [])
            if starting_points:
                for fp in starting_points:
                    flows.append({
                        "page": page_name,
                        "name": fp.get("name", ""),
                        "nodeId": fp.get("nodeId", ""),
                    })
            # Also check the page itself
        page_fps = page.get("flowStartingPoints", [])
        for fp in page_fps:
            flows.append({
                "page": page_name,
                "name": fp.get("name", ""),
                "nodeId": fp.get("nodeId", ""),
            })
    return flows


def cmd_structure(args, token, opener=None):
    """Fetch file structure at controlled depth."""
    file_key = extract_file_key(args.file_key)
    params = {"depth": args.depth}
    if args.node_ids:
        params["ids"] = args.node_ids

    data = api_request(f"/files/{file_key}", token, params, opener=opener)

    document = data.get("document", {})
    cleaned = clean_node(document, depth=args.depth)

    result = {
        "fileName": data.get("name"),
        "lastModified": data.get("lastModified"),
        "version": data.get("version"),
        "document": cleaned,
    }
    print(json.dumps(result, indent=2))


def cmd_interactions(args, token, opener=None):
    """Fetch and extract all interactions and flow starting points."""
    file_key = extract_file_key(args.file_key)
    params = {}
    if args.node_ids:
        params["ids"] = args.node_ids

    data = api_request(f"/files/{file_key}", token, params, opener=opener)
    document = data.get("document", {})

    interactions = []
    for page in document.get("children", []):
        interactions.extend(extract_interactions_from_node(page))

    flows = extract_flow_starting_points(document)

    result = {
        "fileName": data.get("name"),
        "interactions": interactions,
        "flowStartingPoints": flows,
    }
    print(json.dumps(result, indent=2))


def cmd_components(args, token, opener=None):
    """Fetch component metadata: variants, properties, states."""
    file_key = extract_file_key(args.file_key)

    data = api_request(f"/files/{file_key}", token, opener=opener)
    components_meta = data.get("components", {})
    component_sets_meta = data.get("componentSets", {})

    # Build component info
    components = {}
    for comp_id, comp in components_meta.items():
        components[comp_id] = {
            "name": comp.get("name"),
            "description": comp.get("description"),
            "key": comp.get("key"),
            "componentSetId": comp.get("componentSetId"),
            "containingFrame": comp.get("containing_frame", {}).get("name"),
        }

    # Build component set info (variant groups)
    component_sets = {}
    for cs_id, cs in component_sets_meta.items():
        component_sets[cs_id] = {
            "name": cs.get("name"),
            "description": cs.get("description"),
            "key": cs.get("key"),
        }

    # Also extract componentProperties from nodes if node_ids specified
    node_properties = {}
    if args.node_ids:
        node_data = api_request(f"/files/{file_key}/nodes", token, {"ids": args.node_ids}, opener=opener)
        for node_id, node_info in node_data.get("nodes", {}).items():
            doc = node_info.get("document", {})
            props = doc.get("componentProperties", {})
            if props:
                node_properties[node_id] = {
                    "name": doc.get("name"),
                    "properties": {
                        k: {
                            "type": v.get("type"),
                            "defaultValue": v.get("defaultValue"),
                            "variantOptions": v.get("variantOptions"),
                        }
                        for k, v in props.items()
                    },
                }

    result = {
        "fileName": data.get("name"),
        "components": components,
        "componentSets": component_sets,
    }
    if node_properties:
        result["nodeProperties"] = node_properties

    print(json.dumps(result, indent=2))


def cmd_variables(args, token, opener=None):
    """Fetch local variables: booleans, strings, modes."""
    file_key = extract_file_key(args.file_key)

    data = api_request(f"/files/{file_key}/variables/local", token, opener=opener)
    meta = data.get("meta", {})

    variables = {}
    for var_id, var in meta.get("variables", {}).items():
        variables[var_id] = {
            "name": var.get("name"),
            "resolvedType": var.get("resolvedType"),
            "description": var.get("description"),
            "variableCollectionId": var.get("variableCollectionId"),
            "valuesByMode": var.get("valuesByMode"),
            "scopes": var.get("scopes"),
            "hiddenFromPublishing": var.get("hiddenFromPublishing"),
        }

    collections = {}
    for coll_id, coll in meta.get("variableCollections", {}).items():
        collections[coll_id] = {
            "name": coll.get("name"),
            "modes": coll.get("modes"),
            "defaultModeId": coll.get("defaultModeId"),
            "hiddenFromPublishing": coll.get("hiddenFromPublishing"),
        }

    result = {
        "variables": variables,
        "variableCollections": collections,
    }
    print(json.dumps(result, indent=2))


def cmd_comments(args, token, opener=None):
    """Fetch file comments."""
    file_key = extract_file_key(args.file_key)

    data = api_request(f"/files/{file_key}/comments", token, opener=opener)
    comments = []
    for comment in data.get("comments", []):
        comments.append({
            "id": comment.get("id"),
            "message": comment.get("message"),
            "createdAt": comment.get("created_at"),
            "resolvedAt": comment.get("resolved_at"),
            "user": comment.get("user", {}).get("handle"),
            "orderId": comment.get("order_id"),
            "parentId": comment.get("parent_id"),
            "clientMeta": comment.get("client_meta"),
        })

    result = {
        "comments": comments,
    }
    print(json.dumps(result, indent=2))


def cmd_full(args, token, opener=None):
    """Run all extractions combined."""
    file_key = extract_file_key(args.file_key)
    params = {"depth": args.depth}
    if args.node_ids:
        params["ids"] = args.node_ids

    # Fetch main file data
    file_data = api_request(f"/files/{file_key}", token, params, opener=opener)
    document = file_data.get("document", {})

    # Structure
    structure = clean_node(document, depth=args.depth)

    # Interactions
    # Re-fetch without depth limit to get all interactions
    full_data = api_request(f"/files/{file_key}", token,
                            {"ids": args.node_ids} if args.node_ids else None,
                            opener=opener)
    full_doc = full_data.get("document", {})

    interactions = []
    for page in full_doc.get("children", []):
        interactions.extend(extract_interactions_from_node(page))

    flows = extract_flow_starting_points(full_doc)

    # Components
    components_meta = full_data.get("components", {})
    component_sets_meta = full_data.get("componentSets", {})

    components = {}
    for comp_id, comp in components_meta.items():
        components[comp_id] = {
            "name": comp.get("name"),
            "description": comp.get("description"),
            "key": comp.get("key"),
            "componentSetId": comp.get("componentSetId"),
            "containingFrame": comp.get("containing_frame", {}).get("name"),
        }

    component_sets = {}
    for cs_id, cs in component_sets_meta.items():
        component_sets[cs_id] = {
            "name": cs.get("name"),
            "description": cs.get("description"),
            "key": cs.get("key"),
        }

    # Variables (separate endpoint)
    variables_result = {}
    collections_result = {}
    try:
        var_data = api_request(f"/files/{file_key}/variables/local", token, opener=opener)
        meta = var_data.get("meta", {})
        for var_id, var in meta.get("variables", {}).items():
            variables_result[var_id] = {
                "name": var.get("name"),
                "resolvedType": var.get("resolvedType"),
                "description": var.get("description"),
                "variableCollectionId": var.get("variableCollectionId"),
                "valuesByMode": var.get("valuesByMode"),
                "scopes": var.get("scopes"),
            }
        for coll_id, coll in meta.get("variableCollections", {}).items():
            collections_result[coll_id] = {
                "name": coll.get("name"),
                "modes": coll.get("modes"),
                "defaultModeId": coll.get("defaultModeId"),
            }
    except SystemExit:
        # Variables endpoint may fail on older files or without permission
        print("Warning: Could not fetch variables (may require a paid plan)", file=sys.stderr)

    # Comments (separate endpoint)
    comments = []
    try:
        comments_data = api_request(f"/files/{file_key}/comments", token, opener=opener)
        for comment in comments_data.get("comments", []):
            comments.append({
                "id": comment.get("id"),
                "message": comment.get("message"),
                "createdAt": comment.get("created_at"),
                "resolvedAt": comment.get("resolved_at"),
                "user": comment.get("user", {}).get("handle"),
                "parentId": comment.get("parent_id"),
            })
    except SystemExit:
        print("Warning: Could not fetch comments", file=sys.stderr)

    result = {
        "fileName": file_data.get("name"),
        "lastModified": file_data.get("lastModified"),
        "version": file_data.get("version"),
        "structure": structure,
        "interactions": interactions,
        "flowStartingPoints": flows,
        "components": components,
        "componentSets": component_sets,
        "variables": variables_result,
        "variableCollections": collections_result,
        "comments": comments,
    }
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Figma design data for test case generation. "
                    "Outputs functionality-focused JSON, stripping appearance properties.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s structure --file-key ABC123xyz
  %(prog)s interactions --file-key "https://www.figma.com/design/ABC123xyz/My-Project"
  %(prog)s full --file-key ABC123xyz --depth 2
  %(prog)s components --file-key ABC123xyz --node-ids "1:2,3:4"
  %(prog)s structure --file-key ABC123xyz --password SECRET

Environment:
  FIGMA_TOKEN      Figma Personal Access Token (required)
  FIGMA_PASSWORD   Password for password-protected files (optional)
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="What to fetch")
    subparsers.required = True

    # Common arguments
    def add_common_args(sub):
        sub.add_argument(
            "--file-key", required=True,
            help="Figma file key or full Figma URL",
        )
        sub.add_argument(
            "--node-ids",
            help="Comma-separated node IDs to scope the request (e.g., '1:2,3:4')",
        )
        sub.add_argument(
            "--password",
            help="Password for password-protected files (or set FIGMA_PASSWORD env var)",
        )

    # structure
    p_structure = subparsers.add_parser(
        "structure",
        help="Fetch page/frame hierarchy at controlled depth",
    )
    add_common_args(p_structure)
    p_structure.add_argument(
        "--depth", type=int, default=3,
        help="How deep to traverse the node tree (default: 3)",
    )

    # interactions
    p_interactions = subparsers.add_parser(
        "interactions",
        help="Extract interactions, triggers, actions, and flow starting points",
    )
    add_common_args(p_interactions)

    # components
    p_components = subparsers.add_parser(
        "components",
        help="Fetch component metadata (variants, properties, states)",
    )
    add_common_args(p_components)

    # variables
    p_variables = subparsers.add_parser(
        "variables",
        help="Fetch local variables (booleans, strings, modes)",
    )
    add_common_args(p_variables)

    # comments
    p_comments = subparsers.add_parser(
        "comments",
        help="Fetch file comments (often contain behavioral specs)",
    )
    add_common_args(p_comments)

    # full
    p_full = subparsers.add_parser(
        "full",
        help="Run all extractions combined",
    )
    add_common_args(p_full)
    p_full.add_argument(
        "--depth", type=int, default=3,
        help="Depth for structure traversal (default: 3)",
    )

    args = parser.parse_args()

    # Get token
    token = os.environ.get("FIGMA_TOKEN")
    if not token:
        print("Error: FIGMA_TOKEN environment variable is not set.", file=sys.stderr)
        print("Get a Personal Access Token from Figma > Settings > Personal access tokens", file=sys.stderr)
        sys.exit(1)

    # Handle password-protected files
    password = args.password or os.environ.get("FIGMA_PASSWORD")
    opener = None
    if password:
        file_key = extract_file_key(args.file_key)
        opener = build_opener()
        unlock_file(file_key, password, opener)

    # Dispatch
    commands = {
        "structure": cmd_structure,
        "interactions": cmd_interactions,
        "components": cmd_components,
        "variables": cmd_variables,
        "comments": cmd_comments,
        "full": cmd_full,
    }
    commands[args.command](args, token, opener=opener)


if __name__ == "__main__":
    main()

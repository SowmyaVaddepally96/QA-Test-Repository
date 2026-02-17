#!/usr/bin/env python3
"""
Direct Figma API download — no password flow, no rate-limited endpoints.

Fetches file JSON from GET https://api.figma.com/v1/files/:key with X-Figma-Token
and saves it locally. Use this to bypass the password-check flow; works for any
file your token can access (team files, shared links without password).

Usage:
    python figma_download.py <file_key_or_url> [-o output.json]

Requires FIGMA_TOKEN in environment or .env in skill directory.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.figma.com/v1"


def load_env_from_dirs(dirs):
    """Load FIGMA_TOKEN from .env in the given directories."""
    for dir_path in dirs:
        env_path = os.path.join(dir_path, ".env")
        if not os.path.isfile(env_path):
            continue
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line and "FIGMA_TOKEN" in line.split("=", 1)[0]:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key:
                            os.environ.setdefault(key, value)
        except OSError:
            pass
        break


def extract_file_key(key_or_url):
    """Extract file key from a Figma URL or return as-is if already a key."""
    match = re.search(r"figma\.com/(?:design|file)/([a-zA-Z0-9]+)", key_or_url)
    if match:
        return match.group(1)
    return key_or_url.strip()


def download_file(file_key, token, depth=None, node_ids=None):
    """GET /files/:key and return parsed JSON. No password, no cookies."""
    url = f"{BASE_URL}/files/{file_key}"
    params = {}
    if depth is not None:
        params["depth"] = depth
    if node_ids:
        params["ids"] = node_ids
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    req.add_header("X-Figma-Token", token)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Figma API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Figma API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def default_output_path(file_name, file_key, out_dir=None):
    """Default path: out_dir or CWD, filename <safe_name>_<file_key>.json."""
    safe_name = re.sub(r"[^\w\-_. ]", "_", (file_name or "figma").strip())[:50]
    name = f"{safe_name}_{file_key}.json"
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, name)
    return name


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Download Figma file via API (token only, no password) and save locally.",
    )
    parser.add_argument(
        "file_key",
        help="Figma file key or full Figma URL",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON path (default: <fileName>_<fileKey>.json in --output-dir or CWD)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save file in (default: current directory)",
    )
    parser.add_argument(
        "--depth", type=int,
        help="Optional depth limit for document tree",
    )
    parser.add_argument(
        "--node-ids",
        help="Comma-separated node IDs to scope (e.g. 1:2,3:4)",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    load_env_from_dirs([skill_dir, script_dir, os.getcwd()])

    token = os.environ.get("FIGMA_TOKEN")
    if not token:
        print("Error: FIGMA_TOKEN is not set.", file=sys.stderr)
        print("Set it in the environment or in .env in the figma skill directory.", file=sys.stderr)
        sys.exit(1)

    file_key = extract_file_key(args.file_key)
    data = download_file(
        file_key,
        token,
        depth=args.depth,
        node_ids=args.node_ids,
    )

    if args.output:
        output_path = args.output
    else:
        output_path = default_output_path(
            data.get("name", "figma"),
            file_key,
            out_dir=args.output_dir,
        )

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved to {output_path}", file=sys.stderr)
    print(output_path)


if __name__ == "__main__":
    main()

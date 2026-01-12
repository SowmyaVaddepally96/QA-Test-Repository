#!/usr/bin/env python3
"""
Export a Claude agent markdown file with YAML-ish frontmatter into JSON.

Supports the common pattern:
---
key: value
key2: "quoted with \\n escapes"
---
<markdown body>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _unquote_and_unescape(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
        # interpret common backslash escapes like \n, \t, \", \\
        v = bytes(v, "utf-8").decode("unicode_escape")
    return v


def parse_agent_md(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Expected YAML frontmatter starting with '---' on the first line.")

    # Find end of frontmatter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("Expected closing '---' for YAML frontmatter.")

    frontmatter_lines = lines[1:end_idx]
    body_lines = lines[end_idx + 1 :]

    fm: dict[str, str] = {}
    for raw in frontmatter_lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line (missing ':'): {raw}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = _unquote_and_unescape(value)
        fm[key] = value

    # Preserve body exactly as it appeared (minus the frontmatter block),
    # including leading blank lines.
    body = "\n".join(body_lines)
    return fm, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        required=True,
        help="Absolute or relative path to agent .md file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Absolute or relative path to write .json",
    )
    args = parser.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    out_path = Path(args.output).expanduser().resolve()

    text = in_path.read_text(encoding="utf-8")
    fm, body = parse_agent_md(text)

    payload = {
        "source": str(in_path),
        **fm,
        "content": body,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


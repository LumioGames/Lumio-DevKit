#!/usr/bin/env python3
"""Check the official manifest schema, skill metadata and inline Markdown file links.

This is a repository maintenance check, not a client conformance or live SDK test.
Reference-style links, remote URL reachability and Markdown anchors are not checked.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

from jsonschema import Draft202012Validator
import yaml

SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
EXCLUDED = {".git", ".worktrees", ".venv", ".run", "__pycache__"}


def inside(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, RuntimeError, OSError):
        return False


def markdown_links(text):
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, suffix = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is not None:
            continue
        # Destinations may contain underscores/dashes and an optional title.
        for match in re.finditer(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", line):
            yield match.group(1).strip("<>")


def validate(root, schema):
    root = Path(root).resolve()
    errors = []
    count = 0
    manifest = root / "plugin.json"
    try:
        if not inside(manifest, root):
            errors.append("plugin.json: outside package")
        else:
            body = json.loads(manifest.read_text(encoding="utf-8"))
            for error in Draft202012Validator(schema).iter_errors(body):
                errors.append(f"plugin.json: {error.message}")
    except (OSError, ValueError) as error:
        errors.append(f"plugin.json: {error}")

    skills = root / "skills"
    if not skills.is_dir():
        errors.append("skills/: missing directory")
    elif not inside(skills, root):
        errors.append("skills/: outside package")
    else:
        for folder in sorted(skills.iterdir()):
            if folder.name.startswith("."):
                continue
            entry = folder / "SKILL.md"
            label = f"skills/{folder.name}/SKILL.md"
            if not inside(folder, root) or not inside(entry, root):
                errors.append(f"{label}: outside package")
                continue
            if not entry.is_file():
                errors.append(f"{label}: missing SKILL.md entrypoint")
                continue
            try:
                text = entry.read_text(encoding="utf-8")
                match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
                meta = yaml.safe_load(match.group(1)) if match else None
                if not isinstance(meta, dict):
                    errors.append(f"{label}: missing YAML mapping frontmatter")
                    continue
                name, description = meta.get("name"), meta.get("description")
                if (not isinstance(name, str) or len(name) > 64
                        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)):
                    errors.append(f"{label}: invalid skill name")
                if name != folder.name:
                    errors.append(f"{label}: name must match directory")
                if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                    errors.append(f"{label}: description must contain 1–1024 characters")
                if not text[match.end():].strip():
                    errors.append(f"{label}: empty skill body")
                count += 1
            except (OSError, ValueError, yaml.YAMLError) as error:
                errors.append(f"{label}: {error}")

    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in list(dirs) + sorted(files):
            path = Path(directory) / name
            label = path.relative_to(root)
            if not inside(path, root):
                errors.append(f"{label}: resolves outside package")
                continue
            if path.is_symlink() and not path.exists():
                errors.append(f"{label}: broken symlink")
                continue
            if not path.is_file() or path.suffix != ".md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                errors.append(f"{label}: {error}")
                continue
            for target in markdown_links(text):
                if target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                from urllib.parse import unquote
                file_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
                destination = path.parent / file_part
                if file_part.startswith(("/", "\\")) or not inside(destination, root):
                    errors.append(f"{label}: link {target} resolves outside package")
                elif any(p in EXCLUDED for p in destination.resolve().relative_to(root).parts):
                    errors.append(f"{label}: link {target} points into an excluded local directory")
                elif not destination.exists():
                    errors.append(f"{label}: missing link target {target}")
    return errors, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1]/"plugin")
    parser.add_argument("--schema", type=Path, help="Use a downloaded official 1.0.0 schema offline")
    args = parser.parse_args()
    try:
        if args.schema:
            schema = json.loads(args.schema.read_text(encoding="utf-8"))
        else:
            with urllib.request.urlopen(SCHEMA_URL, timeout=20) as response:
                schema = json.load(response)
        if schema.get("$id") != SCHEMA_URL:
            raise ValueError("Expected the official Agent Plugins 1.0.0 manifest schema")
        Draft202012Validator.check_schema(schema)
        errors, count = validate(args.root, schema)
    except Exception as error:
        print(f"CHECK_UNAVAILABLE: {error}", file=sys.stderr)
        return 2
    for error in errors:
        print(error, file=sys.stderr)
    print(f"{'FAIL' if errors else 'PASS'}: skills={count}, issues={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Рендерит templates/prosto-kuhnya.md из data/prosto-kuhnya.json в docs/prosto-kuhnya.md.
Запуск из корня репо: python templates/render_prosto_kuhnya.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root_from_this_file() -> Path:
    return Path(__file__).resolve().parent.parent


def load_episodes(json_path: Path) -> list[dict]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of episodes")
    return data


def render(template_text: str, episodes: list[dict]) -> str:
    try:
        from jinja2 import BaseLoader, Environment
    except ImportError as e:
        raise RuntimeError("jinja2 is not available") from e

    env = Environment(
        loader=BaseLoader(),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    tpl = env.from_string(template_text)
    return tpl.render(episodes=episodes)


def main(argv: list[str]) -> int:
    repo_root = _repo_root_from_this_file()

    p = argparse.ArgumentParser(
        description="Render templates/prosto-kuhnya.md from data/prosto-kuhnya.json to docs/prosto-kuhnya.md"
    )
    p.add_argument(
        "--data",
        type=Path,
        default=repo_root / "data" / "prosto-kuhnya.json",
        help="Path to JSON (default: repo_root/data/prosto-kuhnya.json)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=repo_root / "docs" / "prosto-kuhnya.md",
        help="Output path (default: repo_root/docs/prosto-kuhnya.md)",
    )
    args = p.parse_args(argv)

    if not args.data.exists():
        print(f"ERROR: data file not found: {args.data}", file=sys.stderr)
        return 2

    template_path = repo_root / "templates" / "prosto-kuhnya.md"
    if not template_path.exists():
        print(f"ERROR: template not found: {template_path}", file=sys.stderr)
        return 2

    try:
        episodes = load_episodes(args.data)
    except Exception as e:
        print(f"ERROR: failed loading JSON: {e}", file=sys.stderr)
        return 2

    template_text = template_path.read_text(encoding="utf-8")
    try:
        rendered = render(template_text, episodes)
    except Exception as e:
        print(f"ERROR: failed rendering: {e}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"Wrote {args.out} ({len(episodes)} episodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

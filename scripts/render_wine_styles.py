from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class WineStyle:
    id: int
    title: str
    country_code: str
    vivino_url: str

    def as_template_obj(self) -> dict[str, Any]:
        # Jinja can access dict keys via dot notation as well.
        return {
            "id": self.id,
            "title": self.title,
            "country_code": self.country_code,
            "vivino_url": self.vivino_url,
        }


def _repo_root_from_this_file() -> Path:
    # scripts/render_wine_styles.py -> repo root
    return Path(__file__).resolve().parents[1]


def read_wine_styles(db_path: Path) -> list[WineStyle]:
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, title, country_code, vivino_url
            FROM wine_styles
            ORDER BY country_code, title, id
            """
        )
        rows = cur.fetchall()
    finally:
        con.close()

    styles: list[WineStyle] = []
    for r in rows:
        styles.append(
            WineStyle(
                id=int(r["id"]),
                title=(r["title"] or "").strip(),
                country_code=(r["country_code"] or "").strip(),
                vivino_url=(r["vivino_url"] or "").strip(),
            )
        )
    return styles


def render_with_jinja2(template_text: str, styles: Iterable[WineStyle]) -> str:
    try:
        from jinja2 import BaseLoader, Environment  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("jinja2 is not available") from e

    env = Environment(
        loader=BaseLoader(),
        autoescape=False,  # markdown
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    tpl = env.from_string(template_text)
    return tpl.render(styles=[s.as_template_obj() for s in styles])


def render_minimal_fallback(template_text: str, styles: Iterable[WineStyle]) -> str:
    """
    Minimal renderer supporting ONLY this template pattern:
      {% for style in styles %} ... {{ style.field }} ... {% endfor %}

    This keeps the script usable even if jinja2 isn't installed.
    """
    start_tag = "{% for style in styles %}"
    end_tag = "{% endfor %}"

    if start_tag not in template_text or end_tag not in template_text:
        raise ValueError("Template does not contain expected for/endfor tags")

    pre, rest = template_text.split(start_tag, 1)
    loop_body, post = rest.split(end_tag, 1)

    def substitute(body: str, style: WineStyle) -> str:
        out = body
        out = out.replace("{{ style.id }}", str(style.id))
        out = out.replace("{{ style.title }}", style.title)
        out = out.replace("{{ style.country_code }}", style.country_code)
        out = out.replace("{{ style.vivino_url }}", style.vivino_url)
        return out

    rendered_loop = "".join(substitute(loop_body, s) for s in styles)
    return f"{pre}{rendered_loop}{post}"


def render_template(template_path: Path, styles: list[WineStyle]) -> str:
    template_text = template_path.read_text(encoding="utf-8")
    try:
        return render_with_jinja2(template_text, styles)
    except Exception:
        return render_minimal_fallback(template_text, styles)


def main(argv: list[str]) -> int:
    repo_root = _repo_root_from_this_file()

    p = argparse.ArgumentParser(
        description="Render templates/wine.md from potyk-food.db (wine_styles) into wine_rendered.md"
    )
    p.add_argument(
        "--db",
        type=Path,
        default=repo_root / "potyk-food.db",
        help="Path to SQLite DB (default: repo_root/potyk-food.db)",
    )
    p.add_argument(
        "--template",
        type=Path,
        default=repo_root / "templates" / "wine.md",
        help="Path to template markdown (default: repo_root/templates/wine.md)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=repo_root / "wine_rendered.md",
        help="Output markdown path (default: repo_root/wine_rendered.md)",
    )
    args = p.parse_args(argv)

    db_path: Path = args.db
    template_path: Path = args.template
    out_path: Path = args.out

    if not template_path.exists():
        print(f"ERROR: template not found: {template_path}", file=sys.stderr)
        return 2

    try:
        styles = read_wine_styles(db_path)
    except Exception as e:
        print(f"ERROR: failed reading DB: {e}", file=sys.stderr)
        return 2

    try:
        rendered = render_template(template_path, styles)
    except Exception as e:
        print(f"ERROR: failed rendering template: {e}", file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {out_path} ({len(styles)} styles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


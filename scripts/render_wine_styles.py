from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
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


@dataclass(frozen=True)
class WineWine:
    id: int
    producer: str
    title: str
    style_id: int
    img: str
    review: str
    vivino_url: str

    def as_template_obj(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "producer": self.producer,
            "title": self.title,
            "style_id": self.style_id,
            "img": self.img,
            "review": self.review,
            "vivino_url": self.vivino_url,
        }


@dataclass(frozen=True)
class BeerStyle:
    id: int
    title: str
    country_code: str

    def as_template_obj(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "country_code": self.country_code,
        }


@dataclass(frozen=True)
class BeerBeer:
    id: int
    title: str
    brewery: str
    style_id: int
    review: str
    img: str
    untappd_url: str

    def as_template_obj(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "brewery": self.brewery,
            "style_id": self.style_id,
            "review": self.review,
            "img": self.img,
            "untappd_url": self.untappd_url,
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


def read_wines_by_style_id(db_path: Path) -> dict[int, list[WineWine]]:
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, producer, title, style_id, img, review, vivino_url
            FROM wine_wines
            ORDER BY style_id, id
            """
        )
        rows = cur.fetchall()
    finally:
        con.close()

    grouped: dict[int, list[WineWine]] = defaultdict(list)
    for r in rows:
        style_id_val = r["style_id"]
        if style_id_val is None:
            # Skip unassigned wines; template groups by style_id.
            continue
        grouped[int(style_id_val)].append(
            WineWine(
                id=int(r["id"]),
                producer=(r["producer"] or "").strip(),
                title=(r["title"] or "").strip(),
                style_id=int(style_id_val),
                img=(r["img"] or "").strip(),
                review=(r["review"] or "").strip(),
                vivino_url=(r["vivino_url"] or "").strip(),
            )
        )
    return dict(grouped)


def read_beer_styles(db_path: Path) -> list[BeerStyle]:
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, title, country_code
            FROM beer_styles
            ORDER BY country_code, title, id
            """
        )
        rows = cur.fetchall()
    finally:
        con.close()

    styles: list[BeerStyle] = []
    for r in rows:
        styles.append(
            BeerStyle(
                id=int(r["id"]),
                title=(r["title"] or "").strip(),
                country_code=(r["country_code"] or "").strip(),
            )
        )
    return styles


def read_beers_by_style_id(db_path: Path) -> dict[int, list[BeerBeer]]:
    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, title, brewery, style_id, review, img, untappd_url
            FROM beer_beers
            ORDER BY style_id, id
            """
        )
        rows = cur.fetchall()
    finally:
        con.close()

    grouped: dict[int, list[BeerBeer]] = defaultdict(list)
    for r in rows:
        style_id_val = r["style_id"]
        if style_id_val is None:
            # Skip unassigned beers; template groups by style_id.
            continue
        grouped[int(style_id_val)].append(
            BeerBeer(
                id=int(r["id"]),
                title=(r["title"] or "").strip(),
                brewery=(r["brewery"] or "").strip(),
                style_id=int(style_id_val),
                review=(r["review"] or "").strip(),
                img=(r["img"] or "").strip(),
                untappd_url=(r["untappd_url"] or "").strip(),
            )
        )
    return dict(grouped)


def render_with_jinja2(
    template_text: str,
    styles: Iterable[WineStyle],
    style_wines: dict[int, list[WineWine]],
) -> str:
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
    return tpl.render(
        styles=[s.as_template_obj() for s in styles],
        style_wines={
            int(k): [w.as_template_obj() for w in v] for k, v in style_wines.items()
        },
    )


def _extract_for_block(template_text: str, start_tag: str) -> tuple[str, str, str]:
    """
    Returns (pre, body, post) for a {% for ... %} ... {% endfor %} block,
    handling nested for/endfor pairs.
    """
    if start_tag not in template_text:
        raise ValueError(f"Template does not contain expected tag: {start_tag}")

    start_idx = template_text.index(start_tag)
    pre = template_text[: start_idx + len(start_tag)]
    after_start = template_text[start_idx + len(start_tag) :]

    token_for = "{% for "
    token_end = "{% endfor %}"

    depth = 1
    i = 0
    while i < len(after_start):
        next_for = after_start.find(token_for, i)
        next_end = after_start.find(token_end, i)
        if next_end == -1:
            raise ValueError("Unclosed for-block: missing {% endfor %}")

        if next_for != -1 and next_for < next_end:
            depth += 1
            i = next_for + len(token_for)
            continue

        # next_end is next token
        depth -= 1
        if depth == 0:
            body = after_start[:next_end]
            post = after_start[next_end + len(token_end) :]
            return pre, body, post
        i = next_end + len(token_end)

    raise ValueError("Unclosed for-block: missing {% endfor %}")


def render_minimal_fallback(
    template_text: str,
    styles: Iterable[WineStyle],
    style_wines: dict[int, list[WineWine]],
) -> str:
    """
    Minimal renderer supporting ONLY the patterns used in templates/wine.md:
      {% for style in styles %} ... {% for wine in style_wines[style.id] %} ... {% endfor %} ... {% endfor %}
    """
    outer_start = "{% for style in styles %}"
    inner_start = "{% for wine in style_wines[style.id] %}"

    # Split into: before outer, outer body, after outer.
    outer_pre_text, outer_body, outer_post = _extract_for_block(template_text, outer_start)

    # outer_pre_text currently includes the outer_start tag; remove it.
    pre = outer_pre_text.split(outer_start, 1)[0]

    def subst_style(text: str, style: WineStyle) -> str:
        out = text
        out = out.replace("{{ style.id }}", str(style.id))
        out = out.replace("{{ style.title }}", style.title)
        out = out.replace("{{ style.country_code }}", style.country_code)
        out = out.replace("{{ style.vivino_url }}", style.vivino_url)
        return out

    def subst_wine(text: str, wine: WineWine) -> str:
        out = text
        out = out.replace("{{ wine.id }}", str(wine.id))
        out = out.replace("{{ wine.producer }}", wine.producer)
        out = out.replace("{{ wine.title }}", wine.title)
        out = out.replace("{{ wine.style_id }}", str(wine.style_id))
        out = out.replace("{{ wine.img }}", wine.img)
        out = out.replace("{{ wine.review }}", wine.review)
        out = out.replace("{{ wine.vivino_url }}", wine.vivino_url)
        return out

    rendered_styles: list[str] = []
    for style in styles:
        body_for_style = subst_style(outer_body, style)

        # Render inner wines loop if present.
        if inner_start in body_for_style:
            inner_pre_text, inner_body, inner_post = _extract_for_block(body_for_style, inner_start)
            before_inner = inner_pre_text.split(inner_start, 1)[0]
            wines = style_wines.get(style.id, [])
            rendered_inner = "".join(subst_wine(inner_body, w) for w in wines)
            body_for_style = f"{before_inner}{rendered_inner}{inner_post}"

        rendered_styles.append(body_for_style)

    return f"{pre}{''.join(rendered_styles)}{outer_post}"


def render_beer_with_jinja2(
    template_text: str,
    styles: Iterable[BeerStyle],
    style_beers: dict[int, list[BeerBeer]],
) -> str:
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
    return tpl.render(
        styles=[s.as_template_obj() for s in styles],
        style_beers={
            int(k): [b.as_template_obj() for b in v] for k, v in style_beers.items()
        },
    )


def render_beer_minimal_fallback(
    template_text: str,
    styles: Iterable[BeerStyle],
    style_beers: dict[int, list[BeerBeer]],
) -> str:
    """
    Minimal renderer supporting ONLY the patterns used in templates/beer.md:
      {% for style in styles %} ... {% for beer in style_beers[style.id] %} ... {% endfor %} ... {% endfor %}
    """
    outer_start = "{% for style in styles %}"
    inner_start = "{% for beer in style_beers[style.id] %}"

    # Split into: before outer, outer body, after outer.
    outer_pre_text, outer_body, outer_post = _extract_for_block(template_text, outer_start)

    # outer_pre_text currently includes the outer_start tag; remove it.
    pre = outer_pre_text.split(outer_start, 1)[0]

    def subst_style(text: str, style: BeerStyle) -> str:
        out = text
        out = out.replace("{{ style.id }}", str(style.id))
        out = out.replace("{{ style.title }}", style.title)
        out = out.replace("{{ style.country_code }}", style.country_code)
        return out

    def subst_beer(text: str, beer: BeerBeer) -> str:
        out = text
        out = out.replace("{{ beer.id }}", str(beer.id))
        out = out.replace("{{ beer.title }}", beer.title)
        out = out.replace("{{ beer.brewery }}", beer.brewery)
        out = out.replace("{{ beer.style_id }}", str(beer.style_id))
        out = out.replace("{{ beer.review }}", beer.review)
        out = out.replace("{{ beer.img }}", beer.img)
        out = out.replace("{{ beer.untappd_url }}", beer.untappd_url)
        return out

    rendered_styles: list[str] = []
    for style in styles:
        body_for_style = subst_style(outer_body, style)

        # Render inner beers loop if present.
        if inner_start in body_for_style:
            inner_pre_text, inner_body, inner_post = _extract_for_block(body_for_style, inner_start)
            before_inner = inner_pre_text.split(inner_start, 1)[0]
            beers = style_beers.get(style.id, [])
            rendered_inner = "".join(subst_beer(inner_body, b) for b in beers)
            body_for_style = f"{before_inner}{rendered_inner}{inner_post}"

        rendered_styles.append(body_for_style)

    return f"{pre}{''.join(rendered_styles)}{outer_post}"


def render_template(
    template_path: Path,
    styles: list[WineStyle],
    style_wines: dict[int, list[WineWine]],
) -> str:
    template_text = template_path.read_text(encoding="utf-8")
    try:
        return render_with_jinja2(template_text, styles, style_wines)
    except Exception:
        return render_minimal_fallback(template_text, styles, style_wines)


def render_beer_template(
    template_path: Path,
    styles: list[BeerStyle],
    style_beers: dict[int, list[BeerBeer]],
) -> str:
    template_text = template_path.read_text(encoding="utf-8")
    try:
        return render_beer_with_jinja2(template_text, styles, style_beers)
    except Exception:
        return render_beer_minimal_fallback(template_text, styles, style_beers)


def main(argv: list[str]) -> int:
    repo_root = _repo_root_from_this_file()

    p = argparse.ArgumentParser(
        description="Render templates/wine.md and templates/beer.md from potyk-food.db"
    )
    p.add_argument(
        "--db",
        type=Path,
        default=repo_root / "potyk-food.db",
        help="Path to SQLite DB (default: repo_root/potyk-food.db)",
    )
    args = p.parse_args(argv)

    db_path: Path = args.db

    # Define templates to render
    templates = [
        ("wine", repo_root / "templates" / "wine.md", repo_root / "docs" / "tasting" / "wine.md"),
        ("beer", repo_root / "templates" / "beer.md", repo_root / "docs" / "tasting" / "beer.md"),
    ]

    # Read wine data
    try:
        wine_styles = read_wine_styles(db_path)
        wines_by_style_id = read_wines_by_style_id(db_path)
        for s in wine_styles:
            wines_by_style_id.setdefault(s.id, [])
    except Exception as e:
        print(f"ERROR: failed reading wine data from DB: {e}", file=sys.stderr)
        return 2

    # Read beer data
    try:
        beer_styles = read_beer_styles(db_path)
        beers_by_style_id = read_beers_by_style_id(db_path)
        for s in beer_styles:
            beers_by_style_id.setdefault(s.id, [])
    except Exception as e:
        print(f"ERROR: failed reading beer data from DB: {e}", file=sys.stderr)
        return 2

    # Render both templates
    for template_type, template_path, out_path in templates:
        if not template_path.exists():
            print(f"WARNING: template not found: {template_path}, skipping", file=sys.stderr)
            continue

        try:
            if template_type == "wine":
                rendered = render_template(template_path, wine_styles, wines_by_style_id)
                total_items = sum(len(v) for v in wines_by_style_id.values())
                item_name = "wines"
                styles_count = len(wine_styles)
            else:  # beer
                rendered = render_beer_template(template_path, beer_styles, beers_by_style_id)
                total_items = sum(len(v) for v in beers_by_style_id.values())
                item_name = "beers"
                styles_count = len(beer_styles)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(rendered, encoding="utf-8")
            print(f"Wrote {out_path} ({styles_count} styles, {total_items} {item_name})")
        except Exception as e:
            print(f"ERROR: failed rendering {template_type} template: {e}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


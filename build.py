#!/usr/bin/env python3
"""Render content/exercises.yaml + content/sessions.yaml into public/."""
import argparse
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent

KEYCAP_DIGITS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟",
}


def _item_marker(n):
    return KEYCAP_DIGITS.get(n, f"{n}.")


def render_export_text(session, exercises_by_id, defaults):
    custom_header = session.get("export_header")
    footer = session.get("export_footer") or defaults.get("footer") or ""

    warmup = session["warmup"]
    sections = []
    if custom_header:
        sections.append(custom_header)
    else:
        header_tpl = defaults.get("header") or ""
        if header_tpl:
            sections.append(header_tpl.format(date=session.get("date", ""), label=session.get("label", "")))
            base_url = defaults.get("base_url")
            if base_url:
                sections.append(f"課表詳細連結：{base_url.rstrip('/')}/schedule/{session.get('date', '')}.html")
    sections.append(f"🔥 熱身 {warmup['duration']}：{warmup['note']}")

    block_lines = []
    for i, block in enumerate(session["blocks"], start=1):
        exercise = exercises_by_id[block["exercise_id"]]
        line = f"{_item_marker(i)} {exercise['title_zh']} {block['sets']} 組 x {block['reps']}（休息 {block['rest_seconds']} 秒）"
        detail = exercise.get("summary") or exercise.get("title_en") or ""
        if detail:
            line += f"\n{detail}"
        block_lines.append(line)
    if block_lines:
        sections.append("\n\n".join(block_lines))

    if footer:
        sections.append(footer)

    return "\n\n".join(sections)


def build_index(data, css, env, output_dir, sessions):
    today = date.today().isoformat()
    upcoming_sessions = sorted((s for s in sessions if s["date"] >= today), key=lambda s: s["date"])
    past_sessions = sorted((s for s in sessions if s["date"] < today), key=lambda s: s["date"], reverse=True)

    template = env.get_template("page.html.jinja")
    html = template.render(
        site=data["site"],
        categories=data["categories"],
        upcoming_sessions=upcoming_sessions,
        past_sessions=past_sessions,
        css=css,
    )
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"built {output_dir / 'index.html'}")


def build_sessions(sessions_data, exercises_by_id, css, env, output_dir):
    schedule_dir = output_dir / "schedule"
    schedule_dir.mkdir(parents=True, exist_ok=True)
    template = env.get_template("session.html.jinja")
    sessions = sessions_data["sessions"]
    defaults = sessions_data.get("export_defaults") or {}

    for session in sessions:
        session["export_text"] = render_export_text(session, exercises_by_id, defaults)
        for block in session["blocks"]:
            block["exercise"] = exercises_by_id[block["exercise_id"]]

        html = template.render(session=session, css=css)
        out_path = schedule_dir / f"{session['date']}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"built {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "public"))
    args = parser.parse_args()

    data = yaml.safe_load((ROOT / "content" / "exercises.yaml").read_text(encoding="utf-8"))
    sessions_data = yaml.safe_load((ROOT / "content" / "sessions.yaml").read_text(encoding="utf-8"))
    sessions_data["sessions"].sort(key=lambda s: s["date"], reverse=True)
    sessions = sessions_data["sessions"]
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")

    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exercises_by_id = {ex["id"]: ex for cat in data["categories"] for ex in cat["exercises"]}

    build_index(data, css, env, output_dir, sessions)
    build_sessions(sessions_data, exercises_by_id, css, env, output_dir)


if __name__ == "__main__":
    main()

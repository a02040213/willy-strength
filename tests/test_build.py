import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import render_export_text

EXERCISES_BY_ID = {
    1: {"title_zh": "槓鈴臥推", "title_en": "Barbell Bench Press",
        "summary": "複合推力動作，主練胸大肌、前三角肌與肱三頭肌。"},
    2: {"title_zh": "伏地挺身", "title_en": "Push-up", "summary": None},
}

DEFAULTS = {
    "header": "💪 {date} 重訓課表 {label}",
    "base_url": "https://a02040213.github.io/strength-training/",
    "footer": "如有不適請立即停止。",
}


def make_session(**overrides):
    base = {
        "date": "2026-12-01",
        "label": "推力日",
        "warmup": {"duration": "10 分鐘", "note": "動態伸展"},
        "blocks": [
            {"exercise_id": 1, "sets": 4, "reps": "6-8", "rest_seconds": 120},
            {"exercise_id": 2, "sets": 3, "reps": "12-15", "rest_seconds": 60},
        ],
    }
    base.update(overrides)
    return base


def test_full_session_with_defaults():
    text = render_export_text(make_session(), EXERCISES_BY_ID, DEFAULTS)
    assert text.startswith(
        "💪 2026-12-01 重訓課表 推力日\n\n"
        "課表詳細連結：https://a02040213.github.io/strength-training/schedule/2026-12-01.html\n\n"
        "🔥 熱身 10 分鐘：動態伸展\n\n"
        "1️⃣ 槓鈴臥推 4 組 x 6-8（休息 120 秒）\n"
        "複合推力動作，主練胸大肌、前三角肌與肱三頭肌。\n\n"
        "2️⃣ 伏地挺身 3 組 x 12-15（休息 60 秒）"
    )
    assert text.endswith("如有不適請立即停止。")


def test_block_falls_back_to_title_en_without_summary():
    session = make_session(blocks=[{"exercise_id": 2, "sets": 3, "reps": "12-15", "rest_seconds": 60}])
    text = render_export_text(session, EXERCISES_BY_ID, DEFAULTS)
    assert "1️⃣ 伏地挺身 3 組 x 12-15（休息 60 秒）\nPush-up" in text


def test_per_session_header_footer_overrides_defaults():
    session = make_session(export_header="🏋️ 自訂標題", export_footer="請準時到")
    text = render_export_text(session, EXERCISES_BY_ID, DEFAULTS)
    assert text.startswith("🏋️ 自訂標題\n\n")
    assert text.endswith("請準時到")


def test_build_runs_end_to_end(tmp_path):
    import subprocess

    root = Path(__file__).resolve().parent.parent
    subprocess.run(
        [sys.executable, str(root / "build.py"), "--output-dir", str(tmp_path)],
        check=True, cwd=root,
    )
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "schedule" / "2026-12-01.html").exists()

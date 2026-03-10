import argparse
import csv
import json
import re
from pathlib import Path

from generate_chapter import CHARACTERS, OUT, SETTINGS, build_chapter, get_arc, load_json

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHAPTERS = OUT / "chapters"
META = OUT / "chapter_meta.json"
STATE = DATA / "series_state.json"
SEEDS = DATA / "story_seeds.csv"

SUMMARY_RE = re.compile(r"真琴は(.+?)という異変に向き合い、(.+?)という新しい手がかりを得た。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    return parser.parse_args()


def load_seed_rows() -> list[dict[str, str]]:
    with open(SEEDS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_seed_lookup() -> dict[tuple[str, str], dict[str, str]]:
    lookup = {}
    for row in load_seed_rows():
        lookup[(row["seed"], row["twist"])] = row
    return lookup


def extract_previous_summary(chapter_number: int) -> str:
    if chapter_number <= 1:
        return ""
    chapter_path = CHAPTERS / f"chapter_{chapter_number:03d}.md"
    text = chapter_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 3 and lines[1] == "前回までのあらすじ":
        return lines[2]
    return ""


def extract_seed_for_chapter(chapter_number: int, seed_lookup: dict[tuple[str, str], dict[str, str]]) -> dict[str, str]:
    if chapter_number == 1:
        summary = "真琴は止まった時計の持ち主が毎回違うという異変に向き合い、誰も時計を持ち込んだ記憶がないという新しい手がかりを得た。"
    elif chapter_number == 2:
        summary = "真琴は都市の地下通路に古い作業音が響くという異変に向き合い、誰も使っていないはずの工房が動いているという新しい手がかりを得た。"
    elif chapter_number == 40:
        meta = json.loads(META.read_text(encoding="utf-8"))
        return {
            "seed_id": meta["seed_id"],
            "category": meta["category"],
            "seed": meta["seed"],
            "twist": meta["twist"],
        }
    else:
        next_chapter = CHAPTERS / f"chapter_{chapter_number + 1:03d}.md"
        text = next_chapter.read_text(encoding="utf-8")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        summary = lines[2] if len(lines) >= 3 and lines[1] == "前回までのあらすじ" else ""

    match = SUMMARY_RE.match(summary)
    if not match:
        raise RuntimeError(f"Could not parse summary for chapter {chapter_number}")
    key = (match.group(1), match.group(2))
    seed = seed_lookup.get(key)
    if seed is None:
        raise RuntimeError(f"Could not match seed for chapter {chapter_number}: {key}")
    return seed


def build_state_for_chapter(chapter_number: int, seed_lookup: dict[tuple[str, str], dict[str, str]]) -> dict:
    current = json.loads(STATE.read_text(encoding="utf-8"))
    current["next_chapter"] = chapter_number

    if chapter_number == 1:
        current["last_summary"] = ""
        current["last_seed_id"] = ""
        current["last_seed"] = ""
        current["open_threads"] = []
        current["current_antagonist"] = ""
        return current

    previous_seed = extract_seed_for_chapter(chapter_number - 1, seed_lookup)
    current["last_summary"] = (
        f"真琴は{previous_seed['seed']}という異変に向き合い、"
        f"{previous_seed['twist']}という新しい手がかりを得た。"
    )
    current["last_seed_id"] = previous_seed["seed_id"]
    current["last_seed"] = previous_seed["seed"]
    current["open_threads"] = [previous_seed["twist"]]
    current["current_antagonist"] = "灰島" if chapter_number >= 11 else ""
    return current


def main() -> None:
    args = parse_args()
    settings = load_json(SETTINGS)
    characters = load_json(CHARACTERS)
    seed_lookup = build_seed_lookup()

    for chapter_number in range(args.start, args.end + 1):
        seed = extract_seed_for_chapter(chapter_number, seed_lookup)
        state = build_state_for_chapter(chapter_number, seed_lookup)
        chapter, summary = build_chapter(settings, seed, characters, state)
        chapter_path = CHAPTERS / f"chapter_{chapter_number:03d}.md"
        chapter_path.write_text(chapter, encoding="utf-8")
        if chapter_number == args.end:
            (OUT / "chapter_latest.md").write_text(chapter, encoding="utf-8")
            META.write_text(
                json.dumps(
                    {
                        **seed,
                        "chapter_number": chapter_number,
                        "summary": summary,
                        "character_count": len(chapter),
                        "arc": get_arc(chapter_number),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        print(f"Refreshed chapter_{chapter_number:03d}.md ({len(chapter)} chars)")


if __name__ == "__main__":
    main()

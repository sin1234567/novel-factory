import argparse
import json
from pathlib import Path

from generate_chapter import (
    CHARACTERS,
    OUT,
    SETTINGS,
    STATE,
    build_chapter,
    get_arc,
    load_json,
)

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = OUT / "chapters"
META = OUT / "chapter_meta.json"

SEED_MAP = {
    1: {
        "seed_id": "S001",
        "category": "導入",
        "seed": "止まった時計の持ち主が毎回違う",
        "twist": "誰も時計を持ち込んだ記憶がない",
    },
    2: {
        "seed_id": "S007",
        "category": "秘密",
        "seed": "都市の地下通路に古い作業音が響く",
        "twist": "誰も使っていないはずの工房が動いている",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_numbers", nargs="+", type=int)
    return parser.parse_args()


def build_state(chapter_number: int) -> dict:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["next_chapter"] = chapter_number

    if chapter_number == 1:
        state["last_summary"] = ""
        state["last_seed_id"] = ""
        state["last_seed"] = ""
        state["open_threads"] = []
        state["current_antagonist"] = ""
        return state

    previous_seed = SEED_MAP[chapter_number - 1]
    state["last_summary"] = (
        f"真琴は{previous_seed['seed']}という異変に向き合い、"
        f"{previous_seed['twist']}という新しい手がかりを得た。"
    )
    state["last_seed_id"] = previous_seed["seed_id"]
    state["last_seed"] = previous_seed["seed"]
    state["open_threads"] = [previous_seed["twist"]]
    state["current_antagonist"] = ""
    return state


def main() -> None:
    args = parse_args()
    settings = load_json(SETTINGS)
    characters = load_json(CHARACTERS)

    for chapter_number in args.chapter_numbers:
        seed = SEED_MAP.get(chapter_number)
        if seed is None:
            raise RuntimeError(f"Unsupported chapter for rebuild: {chapter_number}")

        state = build_state(chapter_number)
        chapter, summary = build_chapter(settings, seed, characters, state)
        chapter_file = CHAPTERS / f"chapter_{chapter_number:03d}.md"
        chapter_file.write_text(chapter, encoding="utf-8")

        if chapter_number == args.chapter_numbers[-1]:
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

        print(f"Rebuilt chapter_{chapter_number:03d}.md ({len(chapter)} chars)")


if __name__ == "__main__":
    main()

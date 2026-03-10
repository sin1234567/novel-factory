import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "out" / "chapter_meta.json"
USED = ROOT / "data" / "used_seeds.txt"
STATE = ROOT / "data" / "series_state.json"


def main() -> None:
    if not META.exists():
        raise FileNotFoundError(f"Missing metadata: {META}")

    seed = json.loads(META.read_text(encoding="utf-8"))
    seed_id = seed["seed_id"]

    existing = set()
    if USED.exists():
        existing = {line.strip() for line in USED.read_text(encoding="utf-8").splitlines() if line.strip()}

    if seed_id in existing:
        print(f"Already marked: {seed_id}")
        return

    with open(USED, "a", encoding="utf-8") as f:
        f.write(seed_id + "\n")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["next_chapter"] = seed["chapter_number"] + 1
    state["last_summary"] = seed["summary"]
    state["last_seed_id"] = seed_id
    state["last_seed"] = seed["seed"]

    open_threads = state.get("open_threads", [])
    new_thread = seed["twist"]
    if new_thread not in open_threads:
        open_threads.append(new_thread)
    state["open_threads"] = open_threads[-5:]

    if seed.get("category") in {"対立", "回収"}:
        state["current_antagonist"] = "灰島"

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Marked used: {seed_id}")


if __name__ == "__main__":
    main()

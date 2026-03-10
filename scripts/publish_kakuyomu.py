import json
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
CHAPTERS_DIR = OUT / "chapters"
CONFIG = ROOT / "data" / "publish_config.json"
CHAPTER = OUT / "chapter_latest.md"
AUTH_PROFILE = ROOT / "auth" / "kakuyomu_profile"
UPLOADED = ROOT / "data" / "uploaded_drafts.txt"


def load_config() -> dict:
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def split_chapter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    title = "新しいエピソード"
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
    body = "\n".join(lines[1:]).strip()
    return title, body


def load_uploaded() -> set[str]:
    if not UPLOADED.exists():
        return set()
    with open(UPLOADED, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_uploaded(name: str) -> None:
    with open(UPLOADED, "a", encoding="utf-8") as f:
        f.write(name + "\n")


def iter_pending_chapters() -> list[Path]:
    uploaded = load_uploaded()
    chapters = sorted(CHAPTERS_DIR.glob("chapter_*.md"))
    return [path for path in chapters if path.name not in uploaded]


def main() -> None:
    if not CHAPTER.exists():
        raise FileNotFoundError(f"Missing generated chapter: {CHAPTER}")
    if not AUTH_PROFILE.exists():
        raise FileNotFoundError(f"Missing automation profile: {AUTH_PROFILE}")

    config = load_config()
    episode_url = config.get("work_new_episode_url", "").strip()
    if not episode_url:
        raise RuntimeError("Set work_new_episode_url in data/publish_config.json before publishing.")

    browser = config["browser"]
    user_data_dir = browser["user_data_dir"]
    profile_directory = browser["profile_directory"]
    channel = browser.get("channel", "chrome")

    selectors = config["selectors"]
    pending = iter_pending_chapters()
    if not pending:
        print("No pending chapters to upload.")
        return

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(AUTH_PROFILE),
            headless=False,
            channel=channel,
        )
        for chapter_path in pending:
            title, body = split_chapter(chapter_path.read_text(encoding="utf-8"))
            page = context.new_page()
            page.goto(episode_url, wait_until="domcontentloaded")

            try:
                page.locator(selectors["episode_title"]).fill(title)
                page.locator(selectors["episode_body"]).fill(body)
                page.locator(selectors["save_draft"]).click()
                page.wait_for_timeout(3000)
                save_uploaded(chapter_path.name)
                print(f"Draft saved: {chapter_path.name}")
            except PlaywrightTimeoutError as exc:
                raise RuntimeError(
                    f"Timed out while trying to fill or save the Kakuyomu draft for {chapter_path.name}."
                ) from exc
            finally:
                try:
                    page.close()
                except PlaywrightError:
                    pass

        print("Draft submission flow executed. Verify the saved drafts in Kakuyomu.")
        try:
            context.pages[0].wait_for_timeout(5000)
        except (PlaywrightError, IndexError):
            pass
        context.close()


if __name__ == "__main__":
    main()

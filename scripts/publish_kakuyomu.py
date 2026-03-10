import json
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
CONFIG = ROOT / "data" / "publish_config.json"
CHAPTER = OUT / "chapter_latest.md"
AUTH_PROFILE = ROOT / "auth" / "kakuyomu_profile"


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
    chapter_text = CHAPTER.read_text(encoding="utf-8")
    title, body = split_chapter(chapter_text)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(AUTH_PROFILE),
            headless=False,
            channel=channel,
        )
        page = context.new_page()
        page.goto(episode_url, wait_until="domcontentloaded")

        try:
            page.locator(selectors["episode_title"]).fill(title)
            page.locator(selectors["episode_body"]).fill(body)
            page.locator(selectors["save_draft"]).click()
            page.wait_for_timeout(3000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("Timed out while trying to fill or save the Kakuyomu draft.") from exc

        print("Draft submission flow executed. Verify the result in the opened browser window.")
        input("Press Enter to close the browser...")
        context.close()


if __name__ == "__main__":
    main()

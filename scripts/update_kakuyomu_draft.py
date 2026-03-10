import argparse
import json
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "publish_config.json"
AUTH_PROFILE = ROOT / "auth" / "kakuyomu_profile"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--episode-url", required=True)
    return parser.parse_args()


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
    args = parse_args()
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        raise FileNotFoundError(chapter_path)
    if not AUTH_PROFILE.exists():
        raise FileNotFoundError(f"Missing automation profile: {AUTH_PROFILE}")

    config = load_config()
    selectors = config["selectors"]
    browser = config["browser"]
    title, body = split_chapter(chapter_path.read_text(encoding="utf-8"))

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(AUTH_PROFILE),
            headless=False,
            channel=browser.get("channel", "chrome"),
        )
        page = context.new_page()
        page.goto(args.episode_url, wait_until="domcontentloaded")

        try:
            page.locator(selectors["episode_title"]).fill(title)
            page.locator(selectors["episode_body"]).fill(body)
            page.locator(selectors["save_draft"]).click()
            page.wait_for_timeout(3000)
            print(f"Draft updated: {chapter_path.name}")
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(f"Timed out while updating {chapter_path.name}") from exc
        finally:
            try:
                page.close()
            except PlaywrightError:
                pass
            context.close()


if __name__ == "__main__":
    main()

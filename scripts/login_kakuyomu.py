import os
import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright.sync_api import Error as PlaywrightError

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "publish_config.json"
AUTH_DIR = ROOT / "auth"
AUTH_DIR.mkdir(exist_ok=True)
COPIED_PROFILE = AUTH_DIR / "kakuyomu_profile"


def load_browser_config() -> dict:
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)["browser"]


def main() -> None:
    login_url = os.environ.get("KAKUYOMU_LOGIN_URL", "https://kakuyomu.jp/login")
    browser = load_browser_config()
    source_user_data_dir = Path(browser["user_data_dir"])
    profile_directory = browser["profile_directory"]
    channel = browser.get("channel", "chrome")
    source_profile = source_user_data_dir / profile_directory

    if not source_profile.exists():
        raise FileNotFoundError(f"Chrome profile not found: {source_profile}")

    if COPIED_PROFILE.exists():
        shutil.rmtree(COPIED_PROFILE)
    shutil.copytree(source_profile, COPIED_PROFILE)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(COPIED_PROFILE),
            headless=False,
            channel=channel,
        )
        page = context.new_page()
        page.goto(login_url, wait_until="domcontentloaded")
        print("Copied Chrome profile opened.")
        print("If Kakuyomu is already logged in, just confirm the page and close the browser window.")
        print("If not, log in once and then close the browser window.")
        try:
            page.wait_for_timeout(600000)
        except PlaywrightError:
            pass
        finally:
            try:
                context.close()
            except PlaywrightError:
                pass

    print(f"Saved automation profile: {COPIED_PROFILE}")


if __name__ == "__main__":
    main()

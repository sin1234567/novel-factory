import os
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "publish_config.json"


def load_browser_config() -> dict:
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)["browser"]


def main() -> None:
    login_url = os.environ.get("KAKUYOMU_LOGIN_URL", "https://kakuyomu.jp/login")
    browser = load_browser_config()
    user_data_dir = browser["user_data_dir"]
    profile_directory = browser["profile_directory"]
    channel = browser.get("channel", "chrome")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel=channel,
            args=[f"--profile-directory={profile_directory}"],
        )
        page = context.new_page()
        page.goto(login_url, wait_until="domcontentloaded")
        print("Chrome profile opened.")
        print("If Kakuyomu is already logged in, just confirm the page and close the browser window.")
        print("If not, log in once and then close the browser window.")
        page.wait_for_timeout(600000)
        context.close()

    print(f"Used browser profile: {user_data_dir} / {profile_directory}")


if __name__ == "__main__":
    main()

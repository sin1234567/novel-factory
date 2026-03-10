import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
AUTH_DIR = ROOT / "auth"
AUTH_DIR.mkdir(exist_ok=True)
STORAGE_STATE = AUTH_DIR / "kakuyomu_storage_state.json"


def main() -> None:
    login_url = os.environ.get("KAKUYOMU_LOGIN_URL", "https://kakuyomu.jp/login")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(login_url, wait_until="domcontentloaded")
        print("Log in to Kakuyomu in the opened browser window.")
        print("After login completes and the top page is visible, press Enter here.")
        input()
        context.storage_state(path=str(STORAGE_STATE))
        browser.close()

    print(f"Saved login state: {STORAGE_STATE}")


if __name__ == "__main__":
    main()

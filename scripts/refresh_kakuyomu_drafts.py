import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from update_kakuyomu_draft import AUTH_PROFILE, load_config, split_chapter

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "out" / "chapters"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--work-url", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    selectors = config["selectors"]
    browser = config["browser"]

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(AUTH_PROFILE),
            headless=False,
            channel=browser.get("channel", "chrome"),
        )
        index = context.new_page()
        index.goto(args.work_url, wait_until="domcontentloaded")
        index.wait_for_timeout(3000)

        links = index.locator("a").evaluate_all(
            """els => els.map(e => ({text:(e.innerText||'').trim(), href:e.href}))
            .filter(x => x.href.includes('/episodes/'))"""
        )
        episode_map = {}
        for item in links:
            text = item["text"]
            href = item["href"]
            if text.startswith("第"):
                episode_map[text] = href

        for chapter_number in range(args.start, args.end + 1):
            chapter_path = CHAPTERS / f"chapter_{chapter_number:03d}.md"
            title, body = split_chapter(chapter_path.read_text(encoding="utf-8"))
            episode_url = episode_map.get(title)
            if not episode_url:
                print(f"Skip: {title} (no edit URL found)")
                continue

            page = context.new_page()
            page.goto(episode_url, wait_until="domcontentloaded")
            page.locator(selectors["episode_title"]).fill(title)
            page.locator(selectors["episode_body"]).fill(body)
            page.locator(selectors["save_draft"]).click()
            page.wait_for_timeout(1500)
            page.close()
            print(f"Updated draft: {title}")

        index.close()
        context.close()


if __name__ == "__main__":
    main()

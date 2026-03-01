#!/usr/bin/env python3
"""Capture theme screenshots (mobile + desktop, light + dark).
Requires: pip install playwright && playwright install chromium.
Server must be running: make redeploy then http://localhost:8001 (cluster-a UI)."""
import asyncio
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Install Playwright: pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)

BASE_URL = "http://localhost:8001"
OUT_DIR = "docs/screenshots"

VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "mobile": {"width": 375, "height": 667},
}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for view_name, viewport in VIEWPORTS.items():
            page = await browser.new_page(viewport=viewport)
            # Emulate dark system theme so the page's matchMedia sees it and sets data-theme="dark"
            await page.emulate_media(color_scheme="dark")
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
            except Exception as e:
                print(f"Could not reach {BASE_URL}: {e}", file=sys.stderr)
                print("Run: make redeploy (or make deploy), then try again.", file=sys.stderr)
                await browser.close()
                sys.exit(1)

            # Dark theme (system preference was dark, so page set data-theme="dark")
            await page.screenshot(path=f"{OUT_DIR}/{view_name}-dark.png")
            print(f"Saved {OUT_DIR}/{view_name}-dark.png")

            # Light theme (force so screenshot is light)
            await page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
            await page.screenshot(path=f"{OUT_DIR}/{view_name}-light.png")
            print(f"Saved {OUT_DIR}/{view_name}-light.png")

            await page.close()
        await browser.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())

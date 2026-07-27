"""Capture a screenshot of the running Streamlit app for the README.

Prereq: the app must be running (e.g. `streamlit run app/streamlit_app.py`).
Usage: python scripts/screenshot.py [url] [out_path]
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8503"
out = sys.argv[2] if len(sys.argv) > 2 else "docs/screenshot.png"

with sync_playwright() as p:
    # channel="chrome" uses the OS-installed Google Chrome (no download).
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(
        viewport={"width": 1440, "height": 1180}, device_scale_factor=2
    )
    page.goto(url, wait_until="load", timeout=60000)
    # Streamlit paints after its websocket connects; wait for real content.
    page.wait_for_selector("text=Grand total", timeout=45000)
    page.wait_for_timeout(2500)
    page.screenshot(path=out)
    browser.close()

print(f"saved {out}")

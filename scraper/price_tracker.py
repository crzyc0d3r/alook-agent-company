"""Price tracker for a competitor pricing page.

Standalone version of the scraper the engineer agent ("Theo") builds:
fetches a pricing page, extracts price-like strings, stores a timestamped
snapshot, diffs against the previous snapshot, and prints a change report.
Intended to run on a schedule (e.g., daily at 9am).

If BRIGHTDATA_API_KEY is set, the page is fetched through Bright Data's
Web Unlocker API (avoids IP blocks/CAPTCHAs at scale); otherwise a direct
HTTP request is used. Never commit real API keys.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SNAPSHOT_DIR = Path("snapshots")
PRICE_RE = re.compile(r"\$\s?\d+(?:,\d{3})*(?:\.\d{1,2})?(?:\s*/\s*\w+)?")


def fetch_page(url: str) -> str:
    api_key = os.environ.get("BRIGHTDATA_API_KEY")  # placeholder — set your own
    if api_key:
        # Bright Data Web Unlocker API (see https://github.com/brightdata/cli)
        resp = requests.post(
            "https://api.brightdata.com/request",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"zone": os.environ.get("BRIGHTDATA_ZONE", "web_unlocker1"),
                  "url": url, "format": "raw"},
            timeout=60,
        )
    else:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (price-tracker)"})
    resp.raise_for_status()
    return resp.text


def extract_prices(html: str) -> dict[str, list[str]]:
    """Return price strings grouped by nearby heading/plan context."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    prices = sorted(set(PRICE_RE.findall(text)))
    return {"prices": prices}


def load_previous() -> dict | None:
    snaps = sorted(SNAPSHOT_DIR.glob("*.json"))
    if not snaps:
        return None
    return json.loads(snaps[-1].read_text())


def save_snapshot(data: dict) -> Path:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = SNAPSHOT_DIR / f"{ts}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def diff_report(prev: dict | None, curr: dict) -> str:
    if prev is None:
        return "First run - baseline snapshot recorded. No comparison possible yet."
    old, new = set(prev["prices"]), set(curr["prices"])
    added, removed = new - old, old - new
    if not added and not removed:
        return "No price changes detected."
    lines = ["PRICE CHANGE DETECTED:"]
    if removed:
        lines.append(f"  removed: {sorted(removed)}")
    if added:
        lines.append(f"  added:   {sorted(added)}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Track prices on a pricing page")
    ap.add_argument("--url", default="https://railway.app/pricing")
    args = ap.parse_args()

    html = fetch_page(args.url)
    curr = {"url": args.url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            **extract_prices(html)}
    prev = load_previous()
    report = diff_report(prev, curr)
    path = save_snapshot(curr)
    print(f"Snapshot saved: {path}")
    print(f"Prices found: {curr['prices']}")
    print(report)
    # Non-zero exit on change lets a scheduler (or Ren) trigger a notification.
    return 2 if report.startswith("PRICE CHANGE") else 0


if __name__ == "__main__":
    sys.exit(main())

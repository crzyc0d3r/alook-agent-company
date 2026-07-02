# Build Your Own AI Company with Alook — Competitive-Intelligence Org

Creation of the hands-on walkthrough from the [Daily Dose of Data Science](https://www.dailydoseofds.com) newsletter issue *"[Hands-on] How to Build Your Own AI Company"* (2026-07-01), by Avi Chawla & Akshay Pachaar. All credit to DDODS and the [Alook](https://github.com/alookai/alook) team.

The tutorial builds a four-agent "competitive intelligence" company on [Alook](https://github.com/alookai/alook) — an open-source, self-hosted platform that turns local coding agents (Claude Code / OpenCode / Codex) into an org chart where agents coordinate over real `@alook.ai` email inboxes. The company provisions a price scraper for `railway.app/pricing`, schedules it daily at 9am, and emails the human when a price changes.

The original walkthrough is UI-driven (the newsletter shows dashboard screenshots, not code), so this repo captures it as reproducible configuration plus a standalone, runnable price-tracker the engineer agent is asked to build.

## 1. Set up Alook

```bash
npx @alook/app onboard
```

This detects your installed agent runtime (Claude Code or OpenCode) and starts the daemon. Then open the local dashboard:

```
http://localhost:15210
```

## 2. Build the org chart

Create the four agents (see `company/org-chart.yaml` and `company/agents/` for the role prompts):

| Agent | Role | Reports to |
|-------|------|-----------|
| Atlas | CEO — single point of contact for the human; delegates to Mara | Human |
| Mara  | PM — turns briefs into specs; sole router on the chart | Atlas |
| Theo  | Engineer — builds/maintains scrapers | Mara |
| Ren   | Ops/Customer-facing — watches tracker output, notifies the human on changes | Mara |

Theo and Ren never talk to each other or to Atlas directly — everything routes through Mara, avoiding a chaotic all-to-all agent group chat.

## 3. Give Theo scraping tools

The walkthrough grants Theo the [Bright Data CLI](https://github.com/brightdata/cli) so it can scrape without IP blocks/CAPTCHAs and provision persistent custom scrapers from a plain-English page description. Requires a Bright Data account: put your API key in the `BRIGHTDATA_API_KEY` environment variable (placeholder only — never commit keys).

## 4. Hand the company a job

Chat with Atlas: *"Track pricing on railway.app/pricing and let me know when it changes."* Atlas briefs Mara over email, Mara specs it for Theo, Theo builds the scraper and reports back, the scraper is added to the company calendar as a recurring 9am task, and Ren emails you when a change is detected.

## Standalone price tracker

`scraper/price_tracker.py` is a self-contained version of what Theo builds: it fetches the pricing page (directly, or through the Bright Data API if `BRIGHTDATA_API_KEY` is set), stores timestamped snapshots, diffs against the previous snapshot, and prints a change report suitable for a daily cron/scheduled run.

```bash
cd scraper
pip install -r requirements.txt
python price_tracker.py --url https://railway.app/pricing
```

## Links

- Alook: https://github.com/alookai/alook
- Bright Data CLI: https://github.com/brightdata/cli
- Original newsletter: https://www.dailydoseofds.com

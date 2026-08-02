# Quote of the Day

A small Python script that picks a random quote and sends it once a day via
Discord (preferred) or email (fallback if Discord isn't configured or the
send fails).

## How it works

- Quotes are stored in `data/quotes.json`. When that file is empty, `main.py`
  refills it from the [ZenQuotes](https://zenquotes.io) API, then also tries
  [qapi](https://qapi.vercel.app) and ZenQuotes' single-random endpoint as
  fallbacks if the local file has nothing.
- Each time a quote is picked, it's removed from `data/quotes.json` and
  appended to `archive/quotes.json` so it won't repeat until the pool is
  refilled.
- `data/` and `archive/` are created automatically on first run and are
  git-ignored.

## Setup

```bash
cd quote-of-the-day
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

Create a `.env` file in the project root (git-ignored) with whichever of the
following you intend to use:

| Variable                | Used for | Required for |
|--------------------------|----------|---------------|
| `DISCORD_TOKEN`          | Bot token for the Discord client | Discord delivery |
| `DISCORD_QOD_CHANNEL_ID` | Channel ID to post the quote in | Discord delivery |
| `EMAIL_USERNAME`         | Gmail SMTP username | Email delivery |
| `EMAIL_PASSWORD`         | Gmail SMTP app password | Email delivery |
| `EMAIL_TO`               | Recipient address | Email delivery |
| `EMAIL_CC`               | (optional) CC address | Email delivery |
| `EMAIL_BCC`              | (optional) BCC address | Email delivery |

Run it manually:

```bash
.venv/bin/python main.py
```

## Scheduling

In production this runs once a day at 07:00 via cron. For the full
operational runbook — checking, stopping, restarting, rescheduling, and
debugging the job — see [DEVOPS.md](DEVOPS.md).

# DevOps Runbook — Quote of the Day

Technical reference for whoever operates/maintains the scheduled job. Covers
environment setup, the cron schedule, and how to check, stop, restart,
reschedule, and debug it.

## 1. Environment

- **Interpreter:** project-local virtualenv at `.venv/`, not the system
  Python. All scheduled runs must use `.venv/bin/python`, never a bare
  `python`/`python3`, so the correct dependency versions are used.
- **Working directory:** the job must run with its CWD set to the project
  root (`quote-of-the-day/`). `main.py` reads/writes paths such as
  `data/quotes.json` and `archive/quotes.json` relative to CWD, not relative
  to the script location, so running it from the wrong directory silently
  breaks archiving.
- **Config:** all secrets/config live in `.env` in the project root
  (git-ignored — never commit it). Loaded via `python-dotenv`. See
  [README.md](README.md#2-configure-env) for the variable list.

### (Re)creating the virtualenv

```bash
cd quote-of-the-day
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

### Updating dependencies

```bash
.venv/bin/pip install -r requirements.txt --upgrade
```

## 2. Schedule

The job runs via the **operating system's `cron`**, under the user account
that owns this checkout (currently `godluck`). It is *not* tracked in this
repo — cron state lives outside git, in the OS's crontab — so this document
is the source of truth for what should be configured.

### Current entry

```
0 7 * * * cd /home/godluck/Documents/Programming/godluckz/projects/python/main/quote-of-the-day && /home/godluck/Documents/Programming/godluckz/projects/python/main/quote-of-the-day/.venv/bin/python main.py >> /home/godluck/Documents/Programming/godluckz/projects/python/main/quote-of-the-day/cron.log 2>&1
```

Runs daily at **07:00** (machine local time). Breakdown:

| Part | Purpose |
|---|---|
| `0 7 * * *` | Cron schedule: minute=0, hour=7, every day |
| `cd .../quote-of-the-day &&` | Ensures correct working directory (see §1) |
| `.venv/bin/python main.py` | Runs the script with the project's venv interpreter |
| `>> cron.log 2>&1` | Appends stdout+stderr to `cron.log` (git-ignored) for debugging |

## 3. Checking the job

**Is it scheduled?**
```bash
crontab -l
```
Look for the line above. No output (or the line missing) means it's not
scheduled.

**Did it run, and what happened?**
```bash
tail -n 100 cron.log
```
Every run appends a full log block (directory setup, quote source used,
Discord/email send result). A successful Discord send ends with
`--> Discord Message sent.`; a successful email send with `Email sent
successfully`.

**Did cron itself fire the job** (useful if `cron.log` wasn't touched at
all, which points to a cron-level problem rather than a script problem):
```bash
grep CRON /var/log/syslog        # Debian/Ubuntu
journalctl -u cron --since today # systemd-based distros
```

## 4. Running it manually / forcing a run now

There's no daemon or long-running process to "trigger" — just invoke the
exact same command cron would:

```bash
cd /home/godluck/Documents/Programming/godluckz/projects/python/main/quote-of-the-day
./.venv/bin/python main.py
```

Run this whenever you want an out-of-schedule send (e.g. testing after
changing `.env`). It does not interfere with the next scheduled 07:00 run.

## 5. Stopping / pausing the job

Open the crontab editor:
```bash
crontab -e
```

- **Pause temporarily:** put a `#` at the start of the job's line, save.
- **Resume:** remove the `#`, save.
- **Remove permanently:** delete the line entirely, save.
- **Nuclear option** — wipes *all* cron jobs for this user, not just this
  one; only use if you're sure nothing else depends on this user's
  crontab:
  ```bash
  crontab -r
  ```

Changes take effect immediately — no restart of any service is needed
(there's no persistent process to restart; cron itself only needs to be
running, which it is by default on the OS).

## 6. Changing the schedule

```bash
crontab -e
```

Edit the first two fields (`minute hour`) on the job's line. Format is
`minute hour day month weekday`. Examples:

| Line | Meaning |
|---|---|
| `0 7 * * *` | 07:00 every day *(current)* |
| `30 6 * * *` | 06:30 every day |
| `0 7 * * 1-5` | 07:00, weekdays only |
| `0 7,19 * * *` | 07:00 **and** 19:00 every day |

Save and exit — cron picks up changes automatically, no reload/restart
required.

## 7. Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Nothing in `cron.log` at all | Cron didn't fire the job | `grep CRON /var/log/syslog` — job missing from crontab, cron service down, or machine was off/asleep at 07:00 |
| `cron.log` has output but no message received | `.env` incomplete or wrong | Look for `Fail to send discord message` / `Atleast email to is required.` in the log; verify `.env` values |
| `Fail to send discord message - expected token to be a str, received NoneType` | `DISCORD_TOKEN` or `DISCORD_QOD_CHANNEL_ID` unset | Fill in `.env` |
| Email fallback also silent | `EMAIL_TO` unset, or Gmail rejected the login | Confirm `EMAIL_USERNAME`/`EMAIL_PASSWORD` is a valid Gmail **app password**, not the account password |
| `Fail to get quote from API` messages, but run still completes | An upstream quote API (qapi/zenquotes) was down/rate-limited | Usually self-heals next run; script falls back across three sources before giving up |
| Script runs but paths look wrong / archive not updating | Job wasn't run from the project directory | Confirm the crontab line still has the `cd .../quote-of-the-day &&` prefix intact |

## 8. Machine sleep/power notes

Standard cron does **not** run missed jobs — if the machine is off or
asleep at 07:00, that day's quote is simply skipped (no catch-up run). If
this matters, consider:
- `anacron` (runs missed daily/weekly/monthly jobs after boot), or
- a BIOS/OS wake timer so the machine is awake at 07:00.

Neither is currently configured.

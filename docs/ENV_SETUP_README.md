# How to Load Environment Variables

This guide walks you through loading the project's secret configuration (API keys, etc.) into your terminal so the app can run correctly.

---

## What you need

- A Mac or Linux computer
- The `.env` file in this project folder (ask a developer if you don't have it)
- A terminal window open in this project folder

---

## Step-by-step instructions

### 1. Open Terminal

On Mac: press **Command + Space**, type **Terminal**, and press **Enter**.

### 2. Navigate to the project folder

Type the following and press Enter (adjust the path if your folder is in a different location):

```
cd ~/workspaces/bare_bones_soccer
```

### 3. Load the environment variables

Type the following **exactly** and press Enter:

```
source load_env.sh
```

You should see:

```
Environment variables loaded successfully.
```

That's it! The secret keys are now available in this terminal window for as long as it stays open.

---

## Important notes

- You must use `source load_env.sh`, **not** `./load_env.sh`. The `source` command is what makes the variables available in your terminal session.
- You need to run this **every time** you open a new terminal window.
- Never share the `.env` file or its contents with anyone. It contains live secret keys.
- The `.env` file is already excluded from git, so it will never be accidentally uploaded to GitHub.
- **After editing `.env`, double check the file with something like `awk -F'=' '{print $1}' .env`** — a missing trailing newline on the last line can cause the next value you append to silently merge into the previous line's value (this happened once with `STRIPE_SECRET_KEY`/`LOCAL_SQLITE` and went unnoticed for a while).

## Variables `.env` can define

| Variable | Required? | Notes |
|---|---|---|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Yes | Needed for Zappa deploys and S3 access |
| `SECRET_KEY` | Yes | Django secret key |
| `STRIPE_SECRET_KEY` | Yes | Same live key used on both dev and prod |
| `LOCAL_SQLITE` | No | Set to `1` to run against a local throwaway SQLite DB instead of live Neon — see `docs/WORKFLOW.md` |
| `SSL_CERT_FILE` | No | Only needed if you hit `CERTIFICATE_VERIFY_FAILED` errors sending email locally (common on macOS) |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` | No | Override the default Neon connection details if needed — otherwise the existing values in `barebones/settings.py` are used |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | No | Override the default Gmail sending account if needed |

`zappa_settings.json` (separate from `.env`, also gitignored — see `zappa_settings.json.example` for the shape) is what actually supplies these values to the deployed Lambda for both the `dev` and `prod` stages.

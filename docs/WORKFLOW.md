# Bare Bones Soccer — Dev Workflow Guide

A step-by-step guide for making and deploying changes to the Bare Bones Soccer website.

---

## 1. Open the Project

1. Open **VSCode**
2. File → **Open Folder** → select `bare_bones_soccer`
3. Open the built-in terminal: **Terminal → New Terminal** (or `` Ctrl+` ``)

You should see something like:
```
Ians-Air:bare_bones_soccer ianmarcus$
```
That means you're in the right place.

---

## 2. Activate the Virtual Environment

Every time you open a new terminal, run this first:

```
source .venv/bin/activate
```

You'll know it worked when your terminal prompt changes to show `(.venv)` at the start:
```
((.venv) ) Ians-Air:bare_bones_soccer ianmarcus$
```

> **What this does:** Activates the project's Python environment so all the right packages (Django, Zappa, etc.) are available.

---

## 3. Test Changes Locally

Before pushing anything live, you can preview the site on your own computer.

### Start the local server:
```
python manage.py runserver
```

You'll see output like:
```
Starting development server at http://127.0.0.1:8000/
```

Open your browser and go to **http://127.0.0.1:8000** to see the site running locally.

### Making changes:
- Edit any template (`.html` files in `templates/`) or Python files in VSCode
- The local server **auto-refreshes** — just save the file and reload the browser tab
- No need to restart the server for template changes

### Stop the local server:
Press `Ctrl+C` in the terminal.

> **Important:** The local server is just for you to preview. Nobody else can see it. Nothing goes live until Step 5.

---

## 4. Load Environment Variables

Before deploying to the live site, you need to load your AWS credentials. Do this every time you open a fresh terminal:

```
source load_env.sh
```

You should see:
```
Environment variables loaded successfully.
```

To double-check it worked:
```
echo $AWS_ACCESS_KEY_ID
```
It should print a long string starting with `AKIA...`. If it prints nothing, run `source load_env.sh` again.

> **What this does:** Temporarily loads your secret AWS keys into the terminal session so Zappa can authenticate and push your code to the live site.

---

## 5. Save Changes to GitHub (do this BEFORE deploying)

Commit your work first — `deploy.sh` (see Step 6) will actually refuse to deploy if you have uncommitted changes, so this order matters.

```
git add .
git commit -m "describe what you changed here"
git push
```

**Example commit messages:**
```
git commit -m "update series page with Scheitler pickup location"
git commit -m "add world cup block party teaser to events page"
git commit -m "fix brunch ball ticket pricing"
```

> **What this does:** `git add .` stages all your changed files. `git commit` saves a snapshot with your description. `git push` uploads it to GitHub.

---

## 6. Deploy — Dev First, Then Prod

**There are now two environments.** `dev` is a safe-to-break testing stage on its own URL. `prod` is the real live site at barebonessoccer.com. **They share the same database, Stripe account, and email sending** — dev is for testing that a deploy actually works (no code errors, pages load), not a data/payment sandbox. Don't complete real transactions on dev unless you mean to.

**Step A — push to dev and check it there first:**
```
./deploy.sh dev
```
Then visit **https://as6dpc4s80.execute-api.us-east-2.amazonaws.com/dev/** and click through your changes.

**Step B — once dev looks right, push the same code to the real site:**
```
./deploy.sh prod
```
This will ask you to type `prod` to confirm, since it's the real live site. Once done, visit **barebonessoccer.com** to confirm.

`deploy.sh` handles the safety checks automatically (right branch, no uncommitted changes, no stray untracked files, and the confirmation prompt for prod). If you ever need the raw command instead: `zappa update dev` or `zappa update prod`.

---

## Full Deploy Checklist (Quick Reference)

Every time you make changes, run these in order:

```
source .venv/bin/activate     ← activate environment
source load_env.sh            ← load AWS credentials
git add .                     ← stage changes
git commit -m "your message"  ← save snapshot
git push                      ← upload to GitHub
./deploy.sh dev                ← push to test stage, verify there
./deploy.sh prod                ← push to the real live site
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `command not found: zappa` | Run `source .venv/bin/activate` first |
| `ProfileNotFound: default` | Run `source load_env.sh` first |
| `NoCredentialsError` | Run `source load_env.sh` then retry |
| Changes not showing live | Hard refresh browser: `Cmd+Shift+R` |
| Local server port in use | Run `python manage.py runserver 8001` instead |
| `./deploy.sh` says usage error | You need to specify a stage: `./deploy.sh dev` or `./deploy.sh prod` |

---

## What Lives Where

| Thing | Location |
|---|---|
| HTML templates | `templates/` |
| Static files (images, CSS, JS) | `myapp/static/` |
| Django settings | `barebones/settings.py` (never commit — real secrets, not tracked by git) |
| Zappa deploy config | `zappa_settings.json` (never commit — real secrets, not tracked by git; see `zappa_settings.json.example` for the shape) |
| Environment variables | `.env` (never commit this file) |
| Deploy script | `deploy.sh dev\|prod` |

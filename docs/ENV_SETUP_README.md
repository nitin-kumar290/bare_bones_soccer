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

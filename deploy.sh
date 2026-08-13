#!/bin/bash
# Safe deploy script — refuses to deploy if there are uncommitted changes.
# Usage: ./deploy.sh dev   (test stage, generic URL)
#        ./deploy.sh prod  (real live site — barebonessoccer.com)

set -e

STAGE="$1"
if [ "$STAGE" != "dev" ] && [ "$STAGE" != "prod" ]; then
    echo ""
    echo "ERROR: You must specify a stage."
    echo "Usage: ./deploy.sh dev   or   ./deploy.sh prod"
    echo ""
    exit 1
fi

# Guardrail: these files must never be committed (they hold real secrets and are
# meant to stay local-only). If .gitignore is ever changed/bypassed, refuse to deploy.
for f in zappa_settings.json barebones/settings.py; do
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        echo ""
        echo "ERROR: '$f' is tracked by git. This file contains real secrets and must never be committed."
        echo "Run: git rm --cached $f"
        echo ""
        exit 1
    fi
done

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Must be on main
if [ "$BRANCH" != "main" ]; then
    echo ""
    echo "ERROR: You are on branch '$BRANCH', not 'main'."
    echo "Switch to main before deploying: git checkout main"
    echo ""
    exit 1
fi

# Check for uncommitted changes (tracked files only)
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo ""
    echo "ERROR: You have uncommitted changes. Deploy aborted."
    echo ""
    echo "Files with changes:"
    git status --short
    echo ""
    echo "Commit or stash your changes first, then run ./deploy.sh again."
    echo ""
    exit 1
fi

# Check for untracked files in templates/ or myapp/
UNTRACKED=$(git ls-files --others --exclude-standard templates/ myapp/)
if [ -n "$UNTRACKED" ]; then
    echo ""
    echo "WARNING: Untracked files found that will be bundled into the deploy:"
    echo "$UNTRACKED"
    echo ""
    read -p "Continue anyway? These files should be committed first. (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Deploy cancelled."
        exit 1
    fi
fi

# Extra confirmation specifically for prod — this is the real live site.
if [ "$STAGE" = "prod" ]; then
    echo ""
    echo "You are about to deploy to PRODUCTION (barebonessoccer.com)."
    read -p "Type 'prod' to confirm: " prod_confirm
    if [ "$prod_confirm" != "prod" ]; then
        echo "Deploy cancelled."
        exit 1
    fi
fi

echo ""
echo "Deploying to stage: $STAGE"
echo "Latest commit: $(git log -1 --oneline)"
echo ""

source .venv/bin/activate
zappa update "$STAGE"

echo ""
echo "Deploy complete. Stage: $STAGE"
if [ "$STAGE" = "dev" ]; then
    echo "Test at: https://as6dpc4s80.execute-api.us-east-2.amazonaws.com/dev/"
else
    echo "Live at: https://barebonessoccer.com"
fi

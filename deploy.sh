#!/bin/bash
# Safe deploy script — refuses to deploy if there are uncommitted changes.
# Usage: ./deploy.sh

set -e

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

echo ""
echo "Deploying from branch: $BRANCH"
echo "Latest commit: $(git log -1 --oneline)"
echo ""

source .venv/bin/activate
zappa update dev

echo ""
echo "Deploy complete."

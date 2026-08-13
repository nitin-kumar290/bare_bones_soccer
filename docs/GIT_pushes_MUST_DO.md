## 1. Save Changes to GitHub. You need to do this!

**Commit and push BEFORE deploying**, not after — `deploy.sh` refuses to deploy if you have uncommitted changes, so this has to come first.

```
git add .
git commit -m "describe what you changed here"
git push
```

Then deploy: `./deploy.sh dev` to test, `./deploy.sh prod` to go live. See `docs/WORKFLOW.md` for the full flow.

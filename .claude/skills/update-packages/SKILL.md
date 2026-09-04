---
name: update-packages
description: Update project dependencies to latest versions. Use this skill whenever the user wants to update, bump, upgrade, or check outdated packages — including pnpm-style commands like `pnpm outdated`, `pnpm up -i`, `npm update`, `uv outdated`, `uv lock --upgrade`, or mentions of pyproject.toml, pre-commit, or GitHub Actions versions. Handles oxygen project only.
---

# Update Packages (oxygen project)

Project-local skill to upgrade dependencies to latest. Supports separate scopes so you don't have to update everything at once.

## Commands

Parse the user's argument (default to `all` if missing):

- `all` — update **everything**: `pyproject.toml` + `uv.lock` + `.pre-commit-config.yaml` + `.github/actions/setup/action.yml`
- `pyproject` — only Python deps: `pyproject.toml` → `uv.lock` → `uv sync`
- `pre-commit` — only `.pre-commit-config.yaml` hooks
- `actions` — only `.github/actions/setup/action.yml` (actions/cache, setup-uv)

Examples:
- "update all packages" → `all`
- "bump pyproject to latest" → `pyproject`
- "update pre-commit hooks" → `pre-commit`
- "update github actions" → `actions`

## Workflow

### 1. `pyproject` scope

Why `pyproject.toml` is the source of truth: it holds version *ranges* (`>=`), `uv.lock` holds pinned exact versions. `uv lock --upgrade` only bumps the lock within existing ranges — to change the lower bounds you must edit `pyproject.toml`.

Steps:
1. Run bundled script: `python .claude/skills/update-packages/scripts/update_pyproject.py`
   - Fetches latest from `https://pypi.org/pypi/{name}/json` for each dep in `project.dependencies` and `dependency-groups.dev`
   - Preserves extras like `psycopg[binary]`
   - Rewrites `pyproject.toml` with `>=latest`
   - Runs `uv lock --upgrade` and `uv sync --all-groups`
2. Verify: `uv tree --outdated` should show no `latest:` gaps; `uv pip list --outdated` for venv. Show `git diff pyproject.toml --stat` and `uv.lock` diff.

If the script fails due to network, fall back to manual: `uv tree` to get resolved versions, then regex-replace `pyproject.toml` and run `uv lock --upgrade`.

### 2. `pre-commit` scope

Keep hooks in sync with `pyproject.toml` dev deps:

- `astral-sh/uv-pre-commit` → latest from `https://api.github.com/repos/astral-sh/uv-pre-commit/releases/latest` (currently `0.12.9`)
- `psf/black` → match `black` version in `pyproject.toml` (e.g., `26.5.1`)
- `astral-sh/ruff-pre-commit` → match `ruff` version as `v{version}` (e.g., `v0.16.6`)

Also ensure `language_version: python3.14.7` matches `.python-version`.

Edit `.pre-commit-config.yaml` directly. No `uv lock` needed.

### 3. `actions` scope

Update `.github/actions/setup/action.yml`:

- `actions/cache@v3` → `v4` (check `https://api.github.com/repos/actions/cache/releases/latest`)
- `astral-sh/setup-uv@v5` → `v6` (check `https://api.github.com/repos/astral-sh/setup-uv/releases/latest`)

Keep `python-version: 3.14.7` in sync with `.python-version` and `Dockerfile` `FROM python:3.14.7-alpine`.

### 4. `all` scope

Run all three scopes in order: `pyproject` → `pre-commit` → `actions`. Then:

1. `git diff --stat` to show changed files
2. `uv tree --outdated | head -20` to confirm no major outdated remains
3. Remind user to run `pre-commit run --all-files` or commit will auto-install new hook envs

## Notes

- This skill is **project-local** (oxygen, Python 3.14.7, uv). Don't apply to other projects without confirming paths.
- Major bumps (e.g., `django 5→6`, `pillow 11→12`) can break — after `all`/`pyproject`, suggest running `uv run pytest` or `python manage.py check`.
- If `uv sync` fails with native build errors (e.g., `rpds-py`), the lock may need `uv pip install --no-build-isolation` fallback or the user should pin that transitive dep.

## References

- `scripts/update_pyproject.py` — deterministic updater, use it instead of re-implementing curl loops
- `references/version_map.md` — mapping of pyproject package → pre-commit/action hook counterpart

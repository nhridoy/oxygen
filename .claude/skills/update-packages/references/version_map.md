# Version Mapping (oxygen)

| pyproject package | pre-commit / action counterpart | how to get latest |
|---|---|---|
| `black` | `psf/black` `rev: {version}` | pypi `black` or `api.github.com/repos/psf/black/releases/latest` |
| `ruff` | `astral-sh/ruff-pre-commit` `rev: v{version}` | pypi `ruff` or `api.github.com/repos/astral-sh/ruff-pre-commit/releases/latest` |
| `uv` (via uv-pre-commit) | `astral-sh/uv-pre-commit` `rev: {version}` | `api.github.com/repos/astral-sh/uv-pre-commit/releases/latest` |
| — | `actions/cache` | `api.github.com/repos/actions/cache/releases/latest` → `v4`/`v6` |
| — | `astral-sh/setup-uv` | `api.github.com/repos/astral-sh/setup-uv/releases/latest` → `v6` |

Python version sync: `.python-version` ↔ `pyproject.toml requires-python` ↔ `Dockerfile FROM python:X-alpine` ↔ `.pre-commit-config.yaml language_version` ↔ `.github/actions/setup/action.yml python-version`

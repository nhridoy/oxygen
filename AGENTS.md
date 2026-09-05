# Repository Guidelines

## Project Structure & Module Organization

Oxygen is a Django REST Framework backend with Channels WebSockets. `core/` contains settings, URL/ASGI entry points, shared models, permissions, and middleware. Domain apps are `article/`, `authentications/`, `chat/`, `forum/`, `options/`, `payment/`, `site_settings/`, and `support/`. Keep domain models, views, serializers, migrations, and tests inside their app; larger apps split these into packages. Shared integrations live in `utils/helpers/` and `utils/services/`. Assets are in `static/` and `tinystatic/`; email templates are in `templates/email_templates/`.

## Build, Test, and Development Commands

Use Python matching `pyproject.toml` (currently `>=3.14.7`) and uv. Configure a local `.env` using `.env.dummy` as a reference, preserving any existing configuration.

- `uv sync --locked`: install runtime and development dependencies from `uv.lock`.
- `uv run python manage.py migrate`: apply database migrations.
- `uv run python manage.py runserver`: start the local development server.
- `uv run daphne -b 0.0.0.0 -p 8000 core.asgi:application`: serve ASGI, including WebSockets.
- `uv run pytest`: run the configured test suite.
- `uv run ruff check .` and `uv run ruff format --check .`: check lint and formatting.
- `docker build -t oxygen-backend .`: build the application image.

## Coding Style & Naming Conventions

Use four-space indentation, double quotes, and Ruff’s 88-character formatting target. Ruff checks Python errors and import ordering. Use `snake_case` for modules/functions and `PascalCase` for classes; follow names such as `article_views.py` and `article_serializers.py`. Include migrations with model changes. Use `.pre-commit-config.yaml` for hooks; the legacy `pre-commit.sh` uses Black/isort and automatically stages all files.

## Testing Guidelines

Tests use pytest and pytest-django with `core.settings`. Name files `tests.py`, `test_*.py`, or `*_tests.py`, classes `Test*`, and functions `test_*`. Run focused checks with `uv run pytest authentications/tests.py`. Add regression tests for changed behavior, including validation and permissions. No coverage threshold is configured; CI test execution is currently commented out, so run tests locally.

## Commit & Pull Request Guidelines

History includes `fix:` and `refactor:` prefixes alongside terse maintenance messages. Prefer descriptive, scoped commits. PRs should explain behavior changes, link relevant issues, report validation commands/results, and identify migrations or configuration changes. Include screenshots for visible template/admin changes.

## Security & Configuration

Keep credentials out of commits, including `.env` values and Firebase service-account data. SQLite is the database default; Redis supports caching and channel layers. Configure required services before exercising those features.

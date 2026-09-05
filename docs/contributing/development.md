# Development Workflow

## Inspect and Set Up

Run `git status --short` and inspect the target app, imports, and tests. Preserve existing changes. Read all applicable guides from [AGENTS.md](../../AGENTS.md). Keep changes focused; avoid unrelated formatting or refactoring.

Use Python matching `pyproject.toml` and `.python-version`. Install with `uv sync --locked`; update `pyproject.toml` and `uv.lock` together for intentional dependency changes. Use `.env.dummy` as a configuration reference without overwriting an existing `.env`.

## Commands

| Command | Purpose |
| --- | --- |
| `uv run python manage.py check` | Validate Django configuration |
| `uv run python manage.py migrate` | Apply migrations to the configured development database |
| `uv run python manage.py runserver` | Start the local development server |
| `uv run daphne -b 0.0.0.0 -p 8000 core.asgi:application` | Serve HTTP and WebSockets through ASGI |
| `uv run pytest` | Run configured tests |
| `uv run ruff check .` | Check Python errors and import ordering |
| `uv run ruff format --check .` | Check formatting without modifying files |
| `docker build -t oxygen-backend .` | Build the container image |

SQLite is the default database; Redis supports caching and channel layers. Configure services required by the feature. Compose uses a published image and an external `nginxproxy` network; inspect it before assuming it provides a complete local setup.

## Style and Organization

Use four spaces, double quotes, and Ruff's 88-character formatting target. Use `snake_case` for modules/functions and `PascalCase` for classes. Follow the target app's package layout and explicit `__init__.py` exports. Avoid introducing a module and package with the same name; legacy paths already contain this ambiguity.

Keep domain behavior in its app. Reuse `core/` infrastructure and `utils/services/` integrations. Keep credentials, tokens, personal data, and Firebase service-account contents out of logs and commits.

## Completion

Follow [testing instructions](testing.md), review the diff, and report checks actually run. Documentation changes require link and content verification rather than application tests. Follow [Git instructions](git-and-github.md) for commits and PRs.

## Example: Implement a Category Catalog Increment

For “add a public read-only category catalog,” read the serializers, views, APIs, and testing guides. Their examples form one illustrative implementation. The existing category model can be reused; read the model guide if the task also changes its schema.

Start by inspecting the workspace and installing locked dependencies:

```bash
git status --short
uv sync --locked
uv run python manage.py check
```

Add the catalog serializer and view, export their classes, register the route on the existing article router, and add the API tests. After editing, run:

```bash
uv run ruff check article
uv run ruff format --check article
uv run pytest article/tests.py -k category_catalog
uv run pytest
git diff --check
```

If the model also changes, generate and review its migration as described in [Models](models.md). Report the implemented endpoint and actual check results. Do not report the example as working until its code is implemented and verified.

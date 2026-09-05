# Repository Guidelines

## Read Instructions Before Editing

This file directs contributors and agents to detailed repository instructions. Before changing files, read [Development Workflow](docs/contributing/development.md), then every guide relevant to the task below. Read guides before their corresponding work begins; do not load unrelated guides by default.

| Task | Required guide |
| --- | --- |
| Create or change models, relationships, or migrations | [Models](docs/contributing/models.md) |
| Create or change serializers and input validation | [Serializers](docs/contributing/serializers.md) |
| Create or change views, ViewSets, permissions, or querysets | [Views](docs/contributing/views.md) |
| Add or change endpoints, URLs, or response contracts | [APIs](docs/contributing/apis.md) |
| Write tests or verify changes | [Testing](docs/contributing/testing.md) |
| Create commits, branches, or GitHub pull requests | [Git and GitHub](docs/contributing/git-and-github.md) |

For “create a model,” read the models and testing guides. For a complete CRUD endpoint, read models, serializers, views, APIs, and testing. For “commit the changes,” read the Git and GitHub guide before staging anything.

## Repository Map

Oxygen is a Django REST Framework backend with Channels WebSockets. `core/` holds settings, shared models, permissions, rendering, and ASGI configuration. Domain apps include `article/`, `authentications/`, `chat/`, `forum/`, `options/`, `payment/`, `site_settings/`, and `support/`. Keep domain code, migrations, and tests in their app. Shared helpers and integrations live in `utils/`; assets and templates live in `static/`, `tinystatic/`, and `templates/`.

## Working Rules

Follow the user's current scope and preserve unrelated work. Inspect nearby code and current configuration before implementing; legacy examples may contain behavior that should not be copied. Keep instructions synchronized when conventions change, updating the detailed guide rather than duplicating it here. Report changed behavior, verification results, and checks that could not run. Never claim an unexecuted check passed.

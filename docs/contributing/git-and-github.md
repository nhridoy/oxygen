# Git Commits and GitHub Pull Requests

## Inspect and Preserve Work

Run `git status --short`, `git branch --show-current`, and inspect relevant diffs before Git operations. Preserve unrelated work, including staged changes. Do not discard work, rewrite shared history, or force-push as routine cleanup. Follow the user's authorized scope for commits, pushes, and PR actions.

Inspect the intended base branch and `.github/workflows/` before opening a PR or pushing. Workflows include build, push, and deployment steps; the code-quality workflow is triggered by closed PRs to `dev`. Do not assume workflows are read-only or that `main` is always the correct PR target.

Use descriptive branch names such as `feature/article-search`, `fix/comment-permissions`, or `docs/contributor-guides`, consistent with the team workflow.

## Commit Messages

History includes `fix:` and `refactor:` alongside terse maintenance messages. Use this descriptive convention for new commits:

```text
<type>: <imperative description>

Optional explanation of why the change is needed and relevant constraints.
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, and `chore`. Examples:

```text
feat: add article category filtering
fix: reject comments linked to another article
docs: add task-specific contributor instructions
```

Keep each commit focused on one logical change. Include required tests and migrations with behavior changes. Separate unrelated formatting and dependency upgrades.

## Stage and Verify

Follow [testing instructions](testing.md). Stage explicit paths, then inspect `git diff --cached --stat`, `git diff --cached`, and `git diff --cached --check`. Ensure the staged content contains only intended work and no secrets, database contents, or build output.

Use `.pre-commit-config.yaml` hooks for uv lock consistency and Ruff. Inspect the installed hook before committing: legacy `pre-commit.sh` installs Black/isort plus `git add -A`, which can stage unrelated work. Do not install that legacy script or bypass checks to hide failures. Reinspect hook modifications before retrying a commit.

## Pull Requests and Handoff

Use a descriptive title and explain the problem and resulting behavior. Include relevant issue links, validation commands/results, migration/configuration requirements, and compatibility impact. Include screenshots for visible template/admin changes. Distinguish passed checks from checks not run.

When using `gh` with multiline descriptions, write the body to a temporary file and pass `--body-file`. Review the final diff and required checks before merging. Report commit hashes or PR URLs only after the corresponding operations succeed.

## Example: Commit and Describe a Documentation Change

For an authorized commit containing only model-guide examples, inspect existing staging first, then stage the intended file explicitly:

```bash
git status --short
git diff --cached --stat
git diff -- docs/contributing/models.md
git add docs/contributing/models.md
git diff --cached
git diff --cached --check
git commit -m "docs: add an article category model example"
```

Proceed with the commit only when the entire staged diff belongs to the intended commit. If other work is already staged, preserve it and isolate this commit rather than including it accidentally. The example commands do not authorize committing or pushing when the user has only requested documentation edits.

For a PR covering examples in all contributor guides, use a title such as `docs: add practical contributor guide examples` and a body like:

```markdown
Adds an ArticleCategory model example and connected serializer, view,
API, and test examples so contributors can follow the documented patterns.
Also demonstrates development checks and explicit-path Git staging.

Validation:
- Checked relative documentation links and Python snippet syntax.
- Ran git diff --check.
- Application tests were not run because this change only edits documentation.
```

Replace validation statements with actual results, link a relevant issue if one exists, and use the verified base branch when creating the PR. Do not invent an issue number or claim an example endpoint has shipped.

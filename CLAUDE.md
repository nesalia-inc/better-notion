# better-notion

Always speak in English.

## Development Guidelines

- Use `uv` as the package manager and tool runner
- Continuously test code in depth during development
- Create atomic commits in English at each step

## Build & Publish

- To build the project: `uv build`
- To publish the project: `uv publish` (uses `PYPI_TOKEN` from environment)

## Branch & PR Workflow

For features that could cause problems:
- Create a new branch before starting development
- Analyze potential issues associated with the changes
- Create a PR using the `gh` CLI
- Close an issue using the CLI only after the PR is merged

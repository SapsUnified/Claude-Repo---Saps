# CLAUDE.md — AI Assistant Guide for Claude-Repo---Saps

## Repository Overview

This is the **Claude-Repo---Saps** repository owned by **SapsUnified**. It is currently in its initial setup phase — a skeleton repository ready for development.

- **Primary branch:** `master`
- **Remote:** `origin` (GitHub via SapsUnified organization)

## Repository Structure

```
Claude-Repo---Saps/
├── CLAUDE.md        # This file — AI assistant guidelines
└── README.md        # Project description (placeholder)
```

> **Note:** This repository is newly initialized. Update this section as source code, configuration, and tooling are added.

## Development Workflow

### Branching

- The default branch is `master`.
- Feature branches should follow the pattern: `feature/<description>`
- Bug fix branches: `fix/<description>`
- Claude-assisted branches use: `claude/<description>-<session-id>`

### Commits

- Write clear, descriptive commit messages.
- Use imperative mood (e.g., "Add feature" not "Added feature").
- Keep commits focused — one logical change per commit.

### Pull Requests

- PRs should target `master`.
- Include a summary of changes and testing done.

## Build & Run

No build system, package manager, or dependencies are configured yet. When they are added, document the commands here:

```bash
# Install dependencies
# (not yet configured)

# Run the project
# (not yet configured)

# Run tests
# (not yet configured)

# Lint / format
# (not yet configured)
```

## Testing

No test framework is set up yet. When tests are added:
- Document the test runner and commands here.
- Ensure all tests pass before pushing.

## Code Style & Conventions

No linter or formatter is configured yet. When they are added, follow the project's configured rules. General guidelines:

- Keep code simple and readable.
- Avoid over-engineering — solve the problem at hand.
- Don't add unused imports, dead code, or speculative abstractions.

## CI/CD

No CI/CD pipeline is configured. When one is added, document it here.

## Key Guidelines for AI Assistants

1. **Read before writing.** Always read existing files before modifying them.
2. **Minimal changes.** Only change what is necessary to fulfill the request.
3. **No speculation.** Don't add features, error handling, or abstractions that weren't requested.
4. **Preserve intent.** Respect existing patterns and conventions in the codebase.
5. **Test your work.** Run any available tests/linters before considering work complete.
6. **Don't create unnecessary files.** Prefer editing existing files over creating new ones.
7. **Security first.** Never commit secrets, credentials, or `.env` files.
8. **Keep this file updated.** When the project structure or tooling changes significantly, update CLAUDE.md to reflect the current state.

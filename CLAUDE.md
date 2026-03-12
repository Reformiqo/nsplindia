# CLAUDE.md — nsplindia

## Project Overview

**Repository:** Reformiqo/nsplindia
**Status:** Early-stage project (initialized with README only)

## Repository Structure

```
nsplindia/
├── .git/
├── README.md        # Project readme
└── CLAUDE.md        # This file — guidance for AI assistants
```

## Development Workflow

### Branch Strategy
- **Default branch:** `main`
- Feature branches should follow descriptive naming conventions
- Always create pull requests for code review before merging to `main`

### Git Conventions
- Write clear, descriptive commit messages in imperative mood (e.g., "Add user authentication module")
- Keep commits focused — one logical change per commit
- Do not force-push to shared branches

## Conventions for AI Assistants

- Read existing code before proposing changes
- Do not create files unless necessary — prefer editing existing ones
- Keep changes minimal and focused on the task at hand
- Do not add unnecessary comments, docstrings, or type annotations to unchanged code
- Avoid over-engineering; solve for what is asked, not hypothetical future needs
- Do not commit files containing secrets (`.env`, credentials, API keys)
- Run any available linters or tests before committing

## Notes

This file should be updated as the project evolves — when new frameworks, tools, build systems, or conventions are adopted, reflect them here.

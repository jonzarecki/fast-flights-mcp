# Repository Guidelines

This file provides mandatory instructions for contributors.

## Development workflow

- Use **Python 3.11**.
- Install dependencies with `pip install -e .[dev,test]`.
- Install pre-commit hooks via `pre-commit install`.
- Run tests and linting before committing:
  ```bash
  python -m pytest tests/ -v
  pre-commit run --all-files
  ```
- Ensure linting (ruff) and formatting (black) pass; the configuration sets line length to 130.
- New features require tests, and regression tests are expected for bug fixes.
- Keep coverage from dropping (baseline ~35%).

## File locations

- Source code lives in `src/fast_flights_mcp/`.
- Tests are in `tests/` and must start with `test_`.
- Documentation lives in `docs/`.
- Add exports in `src/fast_flights_mcp/__init__.py` when introducing new modules.

## Pull requests

- Follow the template in `.github/pull_request_template.md`.
- Include a short summary and mark checkboxes after running:
  - `pre-commit run --all-files`
  - `pytest`


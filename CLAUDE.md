# xtp - Claude Code project notes

## Build & install

This project is installed as a CLI tool via [uv](https://docs.astral.sh/uv/):

```bash
# Install (first time)
uv tool install /Users/gonzalodiaz/ws/tools/x-terminal-profiles

# Reinstall after ANY code change (changes don't auto-reload)
uv tool install --reinstall /Users/gonzalodiaz/ws/tools/x-terminal-profiles
```

Always reinstall after making changes — the user expects to test immediately in a new terminal.

## Project structure

- `src/xtp/cli.py` — Argument parsing, command dispatch (the entry point)
- `src/xtp/config.py` — Profile paths, TOML loading/saving, env var builder
- `src/xtp/commands/` — One module per subcommand (create, shell, show, list, etc.)
- `src/xtp/toml_writer.py` — Minimal TOML serializer (stdlib `tomllib` is read-only)
- Profiles live at `~/.config/xtp/profiles/<name>/`

## Key conventions

- Python 3.11+, no external dependencies (stdlib only)
- Build system: hatchling
- Entry point: `xtp = "xtp.cli:main"` (defined in pyproject.toml)
- `XTP_PROFILE` env var is set inside active profile shells — commands can use it to infer the current profile when no name argument is given

## Development workflow

This project follows **test-driven development (TDD)**. When implementing changes:

1. **Write the test first** — add or update tests that describe the expected behavior
2. **Run tests and confirm they fail** — `uv run --group dev pytest -v`
3. **Write the code** to make the tests pass
4. **Refactor** if needed, keeping tests green

## Testing

Run the pytest suite (requires the `dev` dependency group):

```bash
uv run --group dev pytest -v
```

Tests live in `tests/` and use `conftest.py` fixtures that monkeypatch config paths to `tmp_path`, so they never touch `~/.config/xtp/`.

For manual verification after code changes:

```bash
uv tool install --reinstall /Users/gonzalodiaz/ws/tools/x-terminal-profiles
xtp <command> [args]
```

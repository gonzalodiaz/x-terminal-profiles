# tp - Terminal Profiles

Terminal profile manager for multi-client environment isolation. Switch between clients/identities with fully isolated Git, GitHub, Claude Code, Chrome, AWS, and npm configs in a single command.

## The problem

As a consultant or developer working with multiple clients, you constantly juggle:
- Different Git identities (name, email, SSH keys)
- Separate GitHub accounts
- Isolated Claude Code sessions and skills per client
- Different Chrome profiles for OAuth flows
- AWS credentials per client
- npm registries per org

`tp` wraps all of this into named profiles. One command to switch context completely.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install --editable /path/to/terminal-profiles
```

Verify:

```bash
tp --version
```

## Quick start

```bash
# 1. Create a profile (interactive)
tp create acme

# 2. Set up GitHub auth for the profile
tp init-gh acme

# 3. Verify everything is configured
tp verify acme

# 4. Activate the profile
tp shell acme

# You're now in an isolated shell. All git/gh/claude commands
# use the acme identity. Type 'exit' to return.
```

## Commands

| Command | Description |
|---|---|
| `tp create <name>` | Create a new profile interactively |
| `tp shell <name>` | Launch isolated shell with profile environment |
| `tp list` | List all profiles (marks active with `*`) |
| `tp show <name>` | Display profile config and environment variables |
| `tp edit <name>` | Open profile.toml in `$EDITOR` |
| `tp delete <name>` | Delete a profile (with confirmation) |
| `tp current` | Print active profile name |
| `tp verify <name>` | Health check: validate profile setup |
| `tp init-gh <name>` | Authenticate GitHub CLI for a profile |
| `tp init-ssh <name>` | Generate SSH key pair for a profile |
| `tp chrome-profiles` | List available Chrome profiles on the system |

## What gets isolated

When you run `tp shell <name>`, these environment variables are set:

| Variable | Purpose |
|---|---|
| `TP_PROFILE` | Active profile name |
| `TP_PROFILE_DIR` | Path to profile directory |
| `CLAUDE_CONFIG_DIR` | Isolated Claude Code config, history, and skills |
| `GIT_AUTHOR_NAME` / `GIT_COMMITTER_NAME` | Git identity |
| `GIT_AUTHOR_EMAIL` / `GIT_COMMITTER_EMAIL` | Git identity |
| `GIT_SSH_COMMAND` | SSH with profile-specific key (`IdentitiesOnly=yes`) |
| `GH_CONFIG_DIR` | Isolated GitHub CLI auth |
| `BROWSER` | Chrome wrapper that opens URLs in the profile's Chrome user |
| `AWS_PROFILE` / `AWS_CONFIG_FILE` / `AWS_SHARED_CREDENTIALS_FILE` | AWS credentials (if configured) |
| `NPM_CONFIG_USERCONFIG` | npm config (if configured) |

## Profile structure

Profiles live in `~/.config/tp/profiles/<name>/`:

```
~/.config/tp/profiles/acme/
  profile.toml       # Profile configuration
  browser.sh         # Auto-generated Chrome wrapper
  claude/            # Claude Code config, history, skills, memory
    .claude.json     # Onboarding state (seeded from ~/.claude.json)
    settings.json
    skills/          # Global skills for this profile
    projects/        # Per-project Claude settings
    ...
  gh/                # GitHub CLI config (auth tokens)
  aws/               # AWS config and credentials
  npmrc              # npm configuration
```

### profile.toml

```toml
[profile]
description = "Acme Corp"

[git]
author_name = "Your Name"
author_email = "you@acme.com"
ssh_key = "~/.ssh/id_ed25519_acme"

[chrome]
profile_directory = "Profile 3"

[aws]
profile = "acme-dev"

[npm]
isolate = true

[env]
# Custom environment variables
MY_CUSTOM_VAR = "value"
```

## Claude Code integration

Each profile gets its own isolated Claude Code environment: separate conversation history, auto-memory, skills, and project settings.

### Important: onboarding state

Claude Code stores its onboarding flag in `~/.claude.json` (a file in your **home directory root**, not inside `~/.claude/`). When `CLAUDE_CONFIG_DIR` is overridden, Claude looks for `.claude.json` inside that directory instead.

`tp create` automatically seeds this file into new profiles so Claude doesn't show the first-time setup wizard. If you need to seed it manually for an existing profile:

```bash
cp ~/.claude.json ~/.config/tp/profiles/<name>/claude/.claude.json
```

### Migrating an existing Claude setup

To bring your full Claude history, skills, and memory into a profile:

```bash
# Sync everything from your default Claude config
rsync -a ~/.claude/ ~/.config/tp/profiles/<name>/claude/

# Copy the onboarding state
cp ~/.claude.json ~/.config/tp/profiles/<name>/claude/.claude.json
```

### Skills

Claude Code skills can be:
- **Global** (per profile): placed in `~/.config/tp/profiles/<name>/claude/skills/`
- **Project-specific**: placed in `<project>/.claude/skills/`

Global skills are available in every project when using that profile. Project-specific skills stay with the project regardless of which profile is active.

## iTerm2 integration

Add this to your `~/.zshrc` (after `source $ZSH/oh-my-zsh.sh` if using oh-my-zsh) to show the active profile in the iTerm2 tab:

```zsh
# Show active tp profile in iTerm2 tab (title + color)
if [[ -n "$TP_PROFILE" ]]; then
  function _tp_title_precmd() {
    echo -ne "\e]1;tp:${TP_PROFILE}\a"
  }
  precmd_functions+=(_tp_title_precmd)
  # Teal tab color (adjust RGB values to taste)
  echo -ne "\e]6;1;bg;red;brightness;30\a\e]6;1;bg;green;brightness;120\a\e]6;1;bg;blue;brightness;180\a"
fi
```

This sets the tab title to `tp:<profile>` and colors the tab. The color resets automatically when you `exit` the profile shell.

For other terminals, you can use `$TP_PROFILE` in your prompt:

```zsh
if [[ -n "$TP_PROFILE" ]]; then
  RPROMPT="%F{cyan}[tp:$TP_PROFILE]%f"
fi
```

## Development

```bash
# Install from local path
uv tool install /path/to/terminal-profiles

# After making ANY code changes, reinstall (required — changes don't auto-reload)
uv tool install --reinstall /path/to/terminal-profiles
```

# xtp - Terminal Profiles

Terminal profile manager for multi-client environment isolation. Switch between clients/identities with fully isolated Git, GitHub, Claude Code, Chrome, AWS, and npm configs in a single command.

## The problem

As a consultant or developer working with multiple clients, you constantly juggle:
- Different Git identities (name, email, SSH keys)
- Separate GitHub accounts
- Isolated Claude Code sessions and skills per client
- Different Chrome profiles for OAuth flows
- AWS credentials per client
- npm registries per org

`xtp` wraps all of this into named profiles. One command to switch context completely.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install /path/to/x-terminal-profiles
```

Verify:

```bash
xtp --version
```

## Quick start

```bash
# 1. Create a profile (interactive)
xtp create acme

# 2. Set up GitHub auth for the profile
xtp init-gh acme

# 3. Verify everything is configured
xtp verify acme

# 4. Activate the profile
xtp shell acme

# You're now in an isolated shell. All git/gh/claude commands
# use the acme identity. Type 'exit' to return.
```

## Commands

| Command | Description |
|---|---|
| `xtp create <name>` | Create a new profile interactively |
| `xtp shell <name>` | Launch isolated shell with profile environment |
| `xtp list` | List all profiles (marks active with `*`) |
| `xtp show <name>` | Display profile config and environment variables |
| `xtp edit <name>` | Open profile.toml in `$EDITOR` |
| `xtp delete <name>` | Delete a profile (with confirmation) |
| `xtp current` | Print active profile name |
| `xtp verify <name>` | Health check: validate profile setup |
| `xtp init-gh <name>` | Authenticate GitHub CLI for a profile |
| `xtp init-ssh <name>` | Generate SSH key pair for a profile |
| `xtp chrome-profiles` | List available Chrome profiles on the system |

## What gets isolated

When you run `xtp shell <name>`, these environment variables are set:

| Variable | Purpose |
|---|---|
| `XTP_PROFILE` | Active profile name |
| `XTP_PROFILE_DIR` | Path to profile directory |
| `CLAUDE_CONFIG_DIR` | Isolated Claude Code config, history, and skills |
| `GIT_AUTHOR_NAME` / `GIT_COMMITTER_NAME` | Git identity |
| `GIT_AUTHOR_EMAIL` / `GIT_COMMITTER_EMAIL` | Git identity |
| `GIT_SSH_COMMAND` | SSH with profile-specific key (`IdentitiesOnly=yes`) |
| `GH_CONFIG_DIR` | Isolated GitHub CLI auth |
| `BROWSER` | Chrome wrapper that opens URLs in the profile's Chrome user |
| `AWS_PROFILE` / `AWS_CONFIG_FILE` / `AWS_SHARED_CREDENTIALS_FILE` | AWS credentials (if configured) |
| `NPM_CONFIG_USERCONFIG` | npm config (if configured) |

## Profile structure

Profiles live in `~/.config/xtp/profiles/<name>/`:

```
~/.config/xtp/profiles/acme/
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

`xtp create` automatically seeds this file into new profiles so Claude doesn't show the first-time setup wizard. If you need to seed it manually for an existing profile:

```bash
cp ~/.claude.json ~/.config/xtp/profiles/<name>/claude/.claude.json
```

### Migrating an existing Claude setup

To bring your full Claude history, skills, and memory into a profile:

```bash
# Sync everything from your default Claude config
rsync -a ~/.claude/ ~/.config/xtp/profiles/<name>/claude/

# Copy the onboarding state
cp ~/.claude.json ~/.config/xtp/profiles/<name>/claude/.claude.json
```

### Skills

Claude Code skills can be:
- **Global** (per profile): placed in `~/.config/xtp/profiles/<name>/claude/skills/`
- **Project-specific**: placed in `<project>/.claude/skills/`

Global skills are available in every project when using that profile. Project-specific skills stay with the project regardless of which profile is active.

## Shell integration

Add this to your `~/.zshrc` (after `source $ZSH/oh-my-zsh.sh` if using oh-my-zsh) to show the active profile in both the shell prompt and the iTerm2 tab:

```zsh
# Show active xtp profile in iTerm2 tab (title + color) and shell prompt
if [[ -n "$XTP_PROFILE" ]]; then
  function _xtp_title_precmd() {
    echo -ne "\e]1;xtp:${XTP_PROFILE}\a"
  }
  precmd_functions+=(_xtp_title_precmd)
  # Teal tab color (adjust RGB values to taste)
  echo -ne "\e]6;1;bg;red;brightness;30\a\e]6;1;bg;green;brightness;120\a\e]6;1;bg;blue;brightness;180\a"
  RPROMPT="%F{cyan}[xtp:${XTP_PROFILE}]%f"
fi
```

This sets the tab title to `xtp:<profile>`, colors the tab, and shows `[xtp:<profile>]` in cyan on the right side of your prompt. Everything resets automatically when you `exit` the profile shell.

## Development

```bash
# Install from local path
uv tool install /path/to/x-terminal-profiles

# After making ANY code changes, reinstall (required — changes don't auto-reload)
uv tool install --reinstall /path/to/x-terminal-profiles
```

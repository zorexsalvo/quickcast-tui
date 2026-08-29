# Quickcast

A radial menu terminal UI for executing shell scripts ("spells") configured via TOML dotfile. Inspired by Baldur's Gate's quick spell menu.

## Features

- **Radial Menu**: Interactive spell slots arranged in a ring around a central hub
- **Mouse & Keyboard Navigation**: Click buttons or use arrow keys/WASD to navigate
- **Real-time Output**: View command execution output in real-time
- **TOML Configuration**: Define spells in `~/.quickcastrc` or `~/.config/quickcast/spells.toml`
- **Async Execution**: Non-blocking command execution using asyncio
- **Theme Support**: Respects Textual themes with hover and focus effects

## Installation

```bash
pip install quickcast
```

Or install from source:

```bash
git clone https://github.com/zorexsalvo/quickcast-tui
cd quickcast-tui
pip install -e .
```

## Quick Start

Create a configuration file at `~/.quickcastrc`:

```toml
[spell.ls]
name = "List Files"
command = "ls -la"
description = "List files in current directory"

[spell.whoami]
name = "Who Am I"
command = "whoami"
description = "Show current user"
```

Then run:

```bash
python3 -m quickcast.app
```

Navigate the menu with your mouse or arrow keys, click/press Enter to execute a spell.

## User Interface

Spells are drawn as a **radial ring** around a central hub, inspired by Baldur's
Gate's quick spell menu. Each slot shows the spell's emoji icon and name; the hub
shows the currently selected spell with a cast hint. An output overlay floats
over the ring when a spell runs.

```
                         ╔════════════╗
                         ║ List Files ║
                         ║            ║
         ╭────────────╮  ╚════════════╝ ╭────────────╮
         │ Memory     │·················│ Who Am I   │
         │            │·        ·       │            │
         ╰────────────╯         ·       ╰────────────╯
                 ·· ···         ·        ··· ··
                ··    ╔══════════════════╗    ··
                ·     ║     List Files   ║     ·
                ·     ║    ─────────     ║     ·
     ╭────────────╮   ║    List files    ║  ╭────────────╮
     │ Network    │···║                  ║··│ Disk Usage │
     │            │   ║─ Enter to cast ──║  │            │
     ╰────────────╯   ╚══════════════════╝  ╰────────────╯
                   ··      ··       ·      ··
                     ···  ·          ·  ···
                ╭────────────╮···╭────────────╮
                │ Git Status │  ·│ CPU Load   │
                │            │   │            │
                ╰────────────╯   ╰────────────╯

                    ↑↓ navigate   Enter cast
```

**Features:**
- Spell slots arranged in a ring around a central hub
- Each slot shows an emoji icon and its word-wrapped name
- A dotted ring and spokes connect the ring to the hub
- The active slot is highlighted with a gold double-line border
- The hub shows the selected spell's icon, name, description, and cast hint
- Up to 8 spells per page — browse pages with `[` / `]`
- Output overlay appears over the ring while a spell runs
- Click a slot or navigate with arrow keys/WASD to select
- Theme colors adapt to the terminal

For more details, see [RADIAL_MENU_DEMO.txt](https://github.com/zorexsalvo/quickcast-tui/blob/main/RADIAL_MENU_DEMO.txt).

## Configuration

### File Locations

The application looks for configuration in this order:
1. `~/.quickcastrc`
2. `~/.config/quickcast/spells.toml`

### Spell Definition

Each spell is defined as a TOML section:

```toml
[spell.unique_id]
name = "Display Name"
command = "shell command to execute"
description = "Optional description"
icon = "🎯"  # Optional emoji icon
```

### Example Configuration

```toml
[spell.git_status]
name = "Git Status"
command = "git status"
description = "Check git repository status"
icon = "📊"

[spell.disk_usage]
name = "Disk Usage"
command = "df -h"
description = "Show disk usage"
icon = "💾"

[spell.cpu_load]
name = "CPU Load"
command = "top -l 1 | head -n 4"
description = "Show CPU load"
icon = "⚙️"
```

## Controls

- **Mouse**: Click on a spell to execute
- **Arrow Keys / WASD**: Navigate the menu
- **Enter / Space**: Execute selected spell
- **Q / ESC**: Quit application

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## Architecture

- `config.py` - Configuration loading and parsing
- `spell.py` - Spell data model
- `executor.py` - Command execution with subprocess
- `widgets/radial_menu.py` - Radial ring menu widget
- `widgets/output.py` - Output display widget
- `app.py` - Main application

## License

MIT License

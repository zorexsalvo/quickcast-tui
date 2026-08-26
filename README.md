# Quickcast TUI

A radial menu terminal UI for executing shell scripts ("spells") configured via TOML dotfile. Inspired by Baldur's Gate's quick spell menu.

## Features

- **Button-Based Radial Menu**: Interactive spell buttons arranged in a grid with proper Textual styling
- **Mouse & Keyboard Navigation**: Click buttons or use arrow keys/WASD to navigate
- **Real-time Output**: View command execution output in real-time
- **TOML Configuration**: Define spells in `~/.quickcastrc` or `~/.config/quickcast/spells.toml`
- **Async Execution**: Non-blocking command execution using asyncio
- **Theme Support**: Respects Textual themes with hover and focus effects

## Installation

```bash
pip install quickcast-tui
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

The menu uses interactive Textual button widgets arranged in a 5×5 grid:

```
┌────────────────────────────┐
│  👤  📁  🕐  📋  💾       │
│  🌐  ⚙️        ⚡  🔥     │
│  📊        [CENTER]  🎯  💻│
│  🔧  📝  🚀  🛠️  🔄       │
│  💾  🎵  📞  ⌨️  🖱️       │
├────────────────────────────┤
│ 🎯 Who Am I — Show user    │
└────────────────────────────┘
```

**Features:**
- Spell buttons with emoji icons and names
- Click any button to select and execute
- Hover effects for visual feedback
- Selected button shows with primary styling
- Information panel shows current selection
- Keyboard navigation with arrow keys/WASD
- Theme support with responsive colors

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
- `widgets/radial_menu.py` - Radial menu widget with buttons
- `widgets/output.py` - Output display widget
- `app.py` - Main application

## License

MIT License

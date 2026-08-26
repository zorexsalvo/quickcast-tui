# Getting Started with Quickcast

## Installation

### From Source (Development)

```bash
git clone <repository-url>
cd quickcast-tui
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

## Configuration

### 1. Create a Configuration File

Choose one of these locations:
- `~/.quickcastrc` (recommended, simplest)
- `~/.config/quickcast/spells.toml`

### 2. Add Spells

Copy the example configuration and customize it:

```bash
cp examples/spells.toml ~/.quickcastrc
```

Edit `~/.quickcastrc` to add your own commands:

```toml
[spell.whoami]
name = "Who Am I"
command = "whoami"
description = "Show current user"
icon = "👤"

[spell.date]
name = "Date & Time"
command = "date"
description = "Show current date and time"
icon = "🕐"
```

## Running the Application

```bash
# Via module
python3 -m quickcast.app

# Via installed command (if using pip install)
quickcast
```

## Controls

| Input | Action |
|-------|--------|
| **Arrow Keys** or **WASD** | Navigate radial menu |
| **Mouse Click** | Select and execute spell |
| **Enter / Space** | Execute selected spell |
| **Q / ESC** | Quit application |

## Spell Configuration Format

Each spell is defined as a TOML table:

```toml
[spell.unique_id]
name = "Display Name"              # Required: shown in menu
command = "shell command"          # Required: command to execute
description = "Optional description"  # Optional: shown as tooltip
icon = "🎯"                        # Optional: emoji icon (default: ✨)
```

### Examples

Simple command:
```toml
[spell.pwd]
name = "Current Directory"
command = "pwd"
```

Complex command with pipes:
```toml
[spell.ps_top10]
name = "Top 10 Processes"
command = "ps aux | head -10"
```

Git operations:
```toml
[spell.git_status]
name = "Git Status"
command = "git status"
icon = "📊"

[spell.git_log]
name = "Recent Commits"
command = "git log --oneline -5"
icon = "📜"
```

## Testing

Run the test suite:

```bash
python3 -m pytest tests/ -v
```

## Development

### Project Structure

```
src/quickcast/
├── __init__.py          # Package initialization
├── app.py               # Main Textual application
├── config.py            # Configuration loading
├── spell.py             # Spell data model
├── executor.py          # Command execution
└── widgets/
    ├── __init__.py
    ├── radial_menu.py   # Radial menu widget
    └── output.py        # Output display widget

tests/
├── test_config.py       # Config tests
└── test_executor.py     # Executor tests
```

### Code Style

Format code with black:
```bash
black src/ tests/
```

Lint with ruff:
```bash
ruff check src/ tests/
```

## Troubleshooting

### "No configuration file found"
Create a configuration file at `~/.quickcastrc` or `~/.config/quickcast/spells.toml`

### "No spells configured"
Add at least one `[spell.*]` section to your configuration file

### Command output not displaying
Ensure the command produces output. Long-running commands will show output in real-time.

## Features

✓ Visual radial menu (pie/wheel layout)
✓ Mouse and keyboard navigation
✓ TOML configuration
✓ Real-time command output
✓ Async command execution
✓ Error handling and validation


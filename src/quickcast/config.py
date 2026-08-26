"""Configuration loading and parsing for spells."""

import tomllib
from pathlib import Path
from typing import Dict

from .spell import Spell


def _get_config_path() -> Path:
    """Get the configuration file path, checking standard locations."""
    home = Path.home()

    # Check ~/.quickcastrc first
    quickcastrc = home / ".quickcastrc"
    if quickcastrc.exists():
        return quickcastrc

    # Check ~/.config/quickcast/spells.toml
    config_dir = home / ".config" / "quickcast"
    spells_toml = config_dir / "spells.toml"
    if spells_toml.exists():
        return spells_toml

    # Return default location (doesn't need to exist yet)
    return quickcastrc


def load_spells() -> Dict[str, Spell]:
    """Load spells from configuration file.

    Returns:
        Dictionary mapping spell IDs to Spell objects

    Raises:
        FileNotFoundError: If no configuration file is found
        ValueError: If configuration is invalid
    """
    config_path = _get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"No configuration file found. Create one at {config_path} or "
            f"{Path.home() / '.config' / 'quickcast' / 'spells.toml'}"
        )

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    spells: Dict[str, Spell] = {}

    if "spell" in config:
        for spell_id, spell_config in config["spell"].items():
            if not isinstance(spell_config, dict):
                raise ValueError(f"Spell {spell_id} must be a table, got {type(spell_config)}")

            # Validate required fields
            if "name" not in spell_config:
                raise ValueError(f"Spell {spell_id} missing required field 'name'")
            if "command" not in spell_config:
                raise ValueError(f"Spell {spell_id} missing required field 'command'")

            spell = Spell(
                id=spell_id,
                name=spell_config["name"],
                command=spell_config["command"],
                description=spell_config.get("description", ""),
                icon=spell_config.get("icon", "✨"),
                tui=spell_config.get("tui", False),
            )
            spells[spell_id] = spell

    return spells


def get_config_info() -> str:
    """Get information about the current configuration file.

    Returns:
        String describing the configuration file location
    """
    config_path = _get_config_path()
    exists = "exists" if config_path.exists() else "does not exist"
    return f"Configuration: {config_path} ({exists})"

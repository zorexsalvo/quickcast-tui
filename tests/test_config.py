"""Tests for spell configuration loading."""

import tempfile
from pathlib import Path

import pytest

from quickcast.spell import Spell
from quickcast.config import load_spells


def test_spell_creation():
    """Test creating a Spell object."""
    spell = Spell(
        id="test",
        name="Test Spell",
        command="echo test",
        description="A test spell",
        icon="✨"
    )
    assert spell.id == "test"
    assert spell.name == "Test Spell"
    assert spell.command == "echo test"
    assert str(spell) == "✨ Test Spell"


def test_load_spells_from_toml():
    """Test loading spells from TOML configuration."""
    toml_content = """
[spell.test1]
name = "Test Spell 1"
command = "echo test1"
description = "First test spell"
icon = "🎯"

[spell.test2]
name = "Test Spell 2"
command = "echo test2"
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "spells.toml"
        config_file.write_text(toml_content)
        
        # Mock the config path lookup
        import quickcast.config
        original_get_path = quickcast.config._get_config_path
        quickcast.config._get_config_path = lambda: config_file
        
        try:
            spells = load_spells()
            assert len(spells) == 2
            assert "test1" in spells
            assert "test2" in spells
            
            spell1 = spells["test1"]
            assert spell1.name == "Test Spell 1"
            assert spell1.command == "echo test1"
            assert spell1.icon == "🎯"
            
            spell2 = spells["test2"]
            assert spell2.description == ""
            assert spell2.icon == "✨"  # Default icon
        finally:
            quickcast.config._get_config_path = original_get_path


def test_missing_config_file():
    """Test error when config file doesn't exist."""
    import quickcast.config
    original_get_path = quickcast.config._get_config_path
    
    try:
        quickcast.config._get_config_path = lambda: Path("/nonexistent/path/spells.toml")
        with pytest.raises(FileNotFoundError):
            load_spells()
    finally:
        quickcast.config._get_config_path = original_get_path


def test_missing_required_field():
    """Test error when spell is missing required field."""
    toml_content = """
[spell.incomplete]
name = "Incomplete Spell"
# Missing required 'command' field
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "spells.toml"
        config_file.write_text(toml_content)
        
        import quickcast.config
        original_get_path = quickcast.config._get_config_path
        quickcast.config._get_config_path = lambda: config_file
        
        try:
            with pytest.raises(ValueError, match="missing required field"):
                load_spells()
        finally:
            quickcast.config._get_config_path = original_get_path

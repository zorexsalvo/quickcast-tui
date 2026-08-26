"""Quickcast - A radial menu terminal UI for executing shell scripts."""

__version__ = "0.1.0"
__author__ = "Quickcast Contributors"

from .spell import Spell
from .config import load_spells, get_config_info
from .app import QuickcastApp, main

__all__ = ["Spell", "load_spells", "get_config_info", "QuickcastApp", "main"]

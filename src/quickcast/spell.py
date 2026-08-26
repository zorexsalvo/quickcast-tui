"""Data model for spells (shell commands)."""

from dataclasses import dataclass


@dataclass
class Spell:
    """A spell is a configured shell command with metadata."""

    id: str
    name: str
    command: str
    description: str = ""
    icon: str = "✨"
    tui: bool = False  # if True, suspend Quickcast and run command with full terminal access

    def __str__(self) -> str:
        return f"{self.icon} {self.name}"

    def __repr__(self) -> str:
        return f"Spell(id={self.id!r}, name={self.name!r}, command={self.command!r})"

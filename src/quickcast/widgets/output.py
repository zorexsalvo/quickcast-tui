"""Output overlay — floats top-left over the radial menu."""

from typing import Optional

from rich.style import Style
from rich.text import Text
from textual.widgets import Static


class OutputDisplay(Static):
    """Floating output panel shown after spell execution."""

    DEFAULT_CSS = """
    OutputDisplay {
        layer: overlay;
        offset: 1 1;
        width: 56;
        height: 16;
        background: #0a0818;
        border: round #c8961e;
        color: #9090b8;
        padding: 0 1;
        display: none;
    }
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name)
        self._lines: list[str] = []
        self._title: str = ""

    def show_spell(self, spell_name: str, command: str) -> None:
        """Start showing output for a new spell execution."""
        self._title = spell_name
        self._lines = [
            f"[bold #c8961e]► {spell_name}[/]",
            f"[dim #504060]$ {command}[/]",
            "[dim #302040]" + "─" * 50 + "[/]",
        ]
        self.display = True
        self._flush()

    def append_line(self, line: str) -> None:
        self._lines.append(line)
        self._flush()

    def set_text(self, text: str) -> None:
        self._lines = text.splitlines()
        self._flush()

    def clear(self) -> None:
        self._lines = []
        self._flush()

    def hide(self) -> None:
        self.display = False

    def get_text(self) -> str:
        return "\n".join(self._lines)

    def _flush(self) -> None:
        # Keep only the last N lines that fit the visible area (height - 2 borders)
        max_lines = 13
        visible = self._lines[-max_lines:]
        self.update("\n".join(visible))

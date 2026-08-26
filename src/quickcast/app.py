"""Main Quickcast application."""

import asyncio
import subprocess
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual import work

from .config import load_spells, get_config_info
from .spell import Spell
from .executor import execute_spell, ExecutionError
from .widgets import RadialMenu, OutputDisplay


class QuickcastApp(App[None]):
    """Full-screen radial menu with a floating output overlay."""

    TITLE = "Quickcast"
    LAYERS = ("default", "overlay")

    CSS = """
    Screen {
        background: #08081a;
        layers: default overlay;
    }

    Header {
        background: #0e0e28;
        color: #5040a0;
        text-style: bold;
        height: 1;
        dock: top;
    }

    Footer {
        background: #0a0a20;
        color: #252540;
        height: 1;
        dock: bottom;
    }

    RadialMenu {
        layer: default;
        width: 100%;
        height: 100%;
    }

    OutputDisplay {
        layer: overlay;
    }
    """

    BINDINGS = [
        ("q,escape", "quit", "Quit"),
        ("up,w", "select_previous", "Prev"),
        ("down,s", "select_next", "Next"),
        ("left,a", "select_previous", "Prev"),
        ("right,d", "select_next", "Next"),
        ("[", "prev_page", "Prev page"),
        ("]", "next_page", "Next page"),
        ("enter,space", "execute", "Cast"),
        ("x", "close_output", "Close output"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._radial_menu: Optional[RadialMenu] = None
        self._output: Optional[OutputDisplay] = None
        self._executing = False

    def compose(self) -> ComposeResult:
        yield Header()
        spells: list[Spell] = []
        try:
            spells = list(load_spells().values())
        except FileNotFoundError:
            pass

        menu = RadialMenu(spells, on_spell_selected=self._cast_spell)
        self._radial_menu = menu
        yield menu

        output = OutputDisplay()
        self._output = output
        yield output

        yield Footer()

    def on_mount(self) -> None:
        try:
            spells_map = load_spells()
        except FileNotFoundError as e:
            self.notify(str(e), severity="error", timeout=6)
            self.exit(1)
            return

        if not spells_map:
            self.notify(
                "No spells configured. Create ~/.quickcastrc", severity="error", timeout=6
            )
            self.exit(1)
            return

        # Re-populate menu with loaded spells (compose ran before config was read)
        if self._radial_menu:
            self._radial_menu.spells = list(spells_map.values())
            self._radial_menu.refresh()

        self.title = "Quickcast"
        self.sub_title = get_config_info()

    # ── App-level actions (delegated to radial menu) ──────────────────────────

    def action_select_next(self) -> None:
        if self._radial_menu:
            self._radial_menu.action_select_next()

    def action_select_previous(self) -> None:
        if self._radial_menu:
            self._radial_menu.action_select_previous()

    def action_next_page(self) -> None:
        if self._radial_menu:
            self._radial_menu.action_next_page()

    def action_prev_page(self) -> None:
        if self._radial_menu:
            self._radial_menu.action_prev_page()

    def action_execute(self) -> None:
        if self._radial_menu:
            spell = self._radial_menu.get_selected_spell()
            if spell:
                self._cast_spell(spell)

    def action_close_output(self) -> None:
        if self._output:
            self._output.hide()

    # ── Spell execution ───────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _cast_spell(self, spell: Spell) -> None:
        if self._executing:
            return
        self._executing = True

        if spell.tui:
            # Hand the terminal over to the child TUI, then resume when it exits.
            with self.suspend():
                subprocess.run(spell.command, shell=True)
            self._executing = False
            return

        if not self._output:
            self._executing = False
            return
        self._output.show_spell(spell.name, spell.command)

        try:
            async for line in execute_spell(spell):
                self._output.append_line(line)
                await asyncio.sleep(0)
            self._output.append_line("\n[bold #40a060]✓ Done[/]")
        except ExecutionError as e:
            self._output.append_line(f"\n[bold #c04040]✗ {e}[/]")
        finally:
            self._executing = False


def main() -> None:
    QuickcastApp().run()


if __name__ == "__main__":
    main()

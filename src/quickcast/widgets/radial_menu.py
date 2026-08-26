"""BG3-style radial menu — drawn as a Rich canvas, not a widget grid."""

import math
from typing import Optional, Sequence, Callable

from rich.cells import cell_len
from rich.style import Style
from rich.text import Text
from textual.events import Click
from textual.widgets import Static

from ..spell import Spell

PAGE_SIZE = 8
ASPECT = 2.3  # terminal cell width:height ratio (chars are ~2× taller than wide)

# ── BG3-inspired colour palette ──────────────────────────────────────────────
_BG        = "#08081a"
S_BG       = Style(bgcolor=_BG)
S_RING     = Style(color="#1e1e38", bgcolor=_BG)
S_SPOKE    = Style(color="#18182e", bgcolor=_BG)

S_SLOT_BORDER  = Style(color="#2a2a52", bgcolor="#0c0c22")
S_SLOT_TEXT    = Style(color="#505080", bgcolor="#0c0c22")
S_SLOT_BG      = Style(bgcolor="#0c0c22")

S_ACT_BORDER   = Style(color="#c8961e", bgcolor="#1c1400", bold=True)
S_ACT_TEXT     = Style(color="#f0c040", bgcolor="#1c1400", bold=True)

S_HUB_BORDER   = Style(color="#7030b0", bgcolor="#0a0620")
S_HUB_TEXT     = Style(color="#d0a0ff", bgcolor="#0a0620", bold=True)
S_HUB_DIM      = Style(color="#604090", bgcolor="#0a0620")
S_HUB_HINT     = Style(color="#40285a", bgcolor="#0a0620")

S_NAV          = Style(color="#28284a", bgcolor=_BG)


class RadialMenu(Static, can_focus=True):
    """Spell ring drawn entirely as a Rich text canvas.

    Layout (approximate, scales with terminal size):

         ╭── spell ──╮
      ╭──╮           ╭──╮
      │  │   ╔═════╗ │  │
      ╰──╯   ║ hub ║ ╰──╯
             ╚═════╝
      ╭──╮           ╭──╮
      ╰──╯           ╰──╯
         ╰── spell ──╯
    """

    DEFAULT_CSS = """
    RadialMenu {
        width: 100%;
        height: 100%;
        background: #08081a;
    }
    """

    SLOT_W = 14
    SLOT_H = 4
    HUB_W  = 20
    HUB_H  = 7

    def __init__(
        self,
        spells: Sequence[Spell],
        on_spell_selected: Optional[Callable[[Spell], None]] = None,
        name: Optional[str] = None,
    ):
        super().__init__(name=name)
        self.spells = list(spells)
        self.selected_index = 0
        self.on_spell_selected = on_spell_selected
        self._slot_regions: dict[int, tuple[int, int, int, int]] = {}

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def _current_page(self) -> int:
        return self.selected_index // PAGE_SIZE

    @property
    def _total_pages(self) -> int:
        return max(1, (len(self.spells) + PAGE_SIZE - 1) // PAGE_SIZE)

    def _page_spells(self, page: int) -> list[Spell]:
        start = page * PAGE_SIZE
        return self.spells[start : start + PAGE_SIZE]

    def get_selected_spell(self) -> Optional[Spell]:
        if not self.spells or not (0 <= self.selected_index < len(self.spells)):
            return None
        return self.spells[self.selected_index]

    # ── Geometry ──────────────────────────────────────────────────────────────

    def _radii(self, w: int, h: int) -> tuple[int, int]:
        """Return (rx, ry) that maintain a visually circular (not elliptical) layout.

        Both axes are constrained so their ratio equals ASPECT, ensuring the
        ring looks like a perfect circle regardless of terminal dimensions.
        """
        rx = max(6, (w - self.SLOT_W - 4) // 2)
        ry_max = max(3, (h - self.SLOT_H - 2) // 2)
        ry = int(rx / ASPECT)
        if ry > ry_max:
            ry = ry_max
            rx = max(6, int(ry * ASPECT))
        return rx, ry

    def _slot_positions(self, w: int, h: int, n: int) -> list[tuple[int, int]]:
        """Return (x, y) top-left of each spell slot, and populate _slot_regions."""
        cx, cy = w // 2, h // 2
        rx, ry = self._radii(w, h)
        positions = []
        self._slot_regions.clear()
        for i in range(n):
            theta = 2 * math.pi * i / n - math.pi / 2
            sx = int(cx + rx * math.cos(theta)) - self.SLOT_W // 2
            sy = int(cy + ry * math.sin(theta)) - self.SLOT_H // 2
            sx = max(0, min(sx, w - self.SLOT_W))
            sy = max(0, min(sy, h - self.SLOT_H))
            positions.append((sx, sy))
            self._slot_regions[i] = (sx, sy, self.SLOT_W, self.SLOT_H)
        return positions

    def _ring_dots(self, w: int, h: int, slot_pos: list[tuple[int, int]]) -> set[tuple[int, int]]:
        """Points along the ring that connects all slots."""
        if not slot_pos:
            return set()
        cx, cy = w // 2, h // 2
        rx, ry = self._radii(w, h)
        r_ring_x = int(rx * 0.80)
        r_ring_y = int(ry * 0.80)
        dots: set[tuple[int, int]] = set()
        for deg in range(0, 360, 3):
            t = math.radians(deg)
            px = int(cx + r_ring_x * math.cos(t))
            py = int(cy + r_ring_y * math.sin(t))
            if 0 <= px < w and 0 <= py < h:
                dots.add((px, py))
        return dots

    def _spoke_dots(
        self, w: int, h: int, slot_pos: list[tuple[int, int]]
    ) -> set[tuple[int, int]]:
        """Bresenham lines from center to each slot center."""
        if not slot_pos:
            return set()
        cx, cy = w // 2, h // 2
        dots: set[tuple[int, int]] = set()
        endpoints = {(cx, cy)}
        for sx, sy in slot_pos:
            endpoints.add((sx + self.SLOT_W // 2, sy + self.SLOT_H // 2))

        for sx, sy in slot_pos:
            x0, y0 = cx, cy
            x1, y1 = sx + self.SLOT_W // 2, sy + self.SLOT_H // 2
            dx, dy_ = abs(x1 - x0), abs(y1 - y0)
            step_x = 1 if x0 < x1 else -1
            step_y = 1 if y0 < y1 else -1
            err = dx - dy_
            lx, ly = x0, y0
            for _ in range(dx + dy_ + 2):
                if (lx, ly) not in endpoints and 0 <= lx < w and 0 <= ly < h:
                    dots.add((lx, ly))
                if lx == x1 and ly == y1:
                    break
                e2 = 2 * err
                if e2 > -dy_:
                    err -= dy_
                    lx += step_x
                if e2 < dx:
                    err += dx
                    ly += step_y
        return dots

    # ── Slot / hub row builders ───────────────────────────────────────────────

    def _slot_row(
        self, row_i: int, spell: Spell, is_active: bool
    ) -> Text:
        """Return Rich Text of exactly SLOT_W display columns for row `row_i`.

        Two content rows are used so long names word-wrap instead of cropping:
          row 0  ╭──────────────╮
          row 1  │ 🔥 First wor │
          row 2  │ ds of name   │
          row 3  ╰──────────────╯
        """
        bdr = S_ACT_BORDER if is_active else S_SLOT_BORDER
        txt = S_ACT_TEXT if is_active else S_SLOT_TEXT
        tl, tr, bl, br = ("╔", "╗", "╚", "╝") if is_active else ("╭", "╮", "╰", "╯")
        hz = "═" if is_active else "─"
        vt = "║" if is_active else "│"
        inner = self.SLOT_W - 2

        t = Text()
        if row_i == 0:
            t.append(tl + hz * inner + tr, style=bdr)
            return t
        if row_i == self.SLOT_H - 1:
            t.append(bl + hz * inner + br, style=bdr)
            return t

        # Split name across two content rows, preferring word boundaries.
        icon = spell.icon
        icon_w = cell_len(icon)
        line1_avail = max(1, inner - icon_w - 1)  # space after icon on row 1
        line2_avail = inner

        name = spell.name
        if cell_len(name) <= line1_avail:
            line1, line2 = name, ""
        else:
            boundary = name.rfind(" ", 0, line1_avail + 1)
            if boundary > 0:
                line1, line2 = name[:boundary], name[boundary + 1:]
            else:
                line1, line2 = name[:line1_avail], name[line1_avail:]
            line2 = line2[:line2_avail]

        t.append(vt, style=bdr)
        if row_i == 1:
            content = f"{icon} {line1}"
            pad = max(0, inner - cell_len(content))
            t.append(content + " " * pad, style=txt)
        else:  # row_i == 2
            pad = max(0, inner - cell_len(line2))
            t.append(line2 + " " * pad, style=txt)
        t.append(vt, style=bdr)
        return t

    def _hub_row(self, row_i: int) -> Text:
        """Return Rich Text of exactly HUB_W display columns for row `row_i`."""
        spell = self.get_selected_spell()
        inner = self.HUB_W - 2
        t = Text()

        if row_i == 0:
            t.append("╔" + "═" * inner + "╗", style=S_HUB_BORDER)
            return t
        if row_i == self.HUB_H - 1:
            t.append("╚" + "═" * inner + "╝", style=S_HUB_BORDER)
            return t

        def _center(s: str, width: int, style: Style) -> Text:
            cells = cell_len(s)
            left = max(0, (width - cells) // 2)
            right = max(0, width - cells - left)
            out = Text()
            out.append(" " * left + s + " " * right, style=style)
            return out

        content_row = row_i - 1
        if not spell:
            lines = [
                ("", S_HUB_DIM),
                ("⚡  QUICKCAST", S_HUB_TEXT),
                ("", S_HUB_DIM),
                ("", S_HUB_DIM),
                ("↑↓ select  Enter cast", S_HUB_HINT),
            ]
        else:
            desc = spell.description[:inner - 2] if spell.description else ""
            lines = [
                (f"{spell.icon}  {spell.name[:inner - 4]}", S_HUB_TEXT),
                ("─" * (inner // 2), S_HUB_DIM),
                (desc, S_HUB_DIM),
                ("", S_HUB_DIM),
                ("── Enter to cast ──", S_HUB_HINT),
            ]

        t.append("║", style=S_HUB_BORDER)
        if content_row < len(lines):
            label, style = lines[content_row]
            t.append_text(_center(label, inner, style))
        else:
            t.append(" " * inner, style=S_HUB_DIM)
        t.append("║", style=S_HUB_BORDER)
        return t

    # ── Main render ───────────────────────────────────────────────────────────

    def render(self) -> Text:  # type: ignore[override]
        w, h = self.size.width, self.size.height
        if w < 20 or h < 8:
            return Text("...")

        page_spells = self._page_spells(self._current_page)
        n = len(page_spells)
        slot_pos = self._slot_positions(w, h, n)
        ring = self._ring_dots(w, h, slot_pos)
        spokes = self._spoke_dots(w, h, slot_pos)

        cx, cy = w // 2, h // 2
        hub_x = max(0, cx - self.HUB_W // 2)
        hub_y = max(0, cy - self.HUB_H // 2)

        result = Text()
        for y in range(h):
            result.append_text(
                self._build_row(
                    y, w, page_spells, slot_pos, ring, spokes, hub_x, hub_y
                )
            )
            if y < h - 1:
                result.append("\n")

        # Navigation hint at very bottom centre
        if self._total_pages > 1:
            hint = f"[ ] page {self._current_page + 1}/{self._total_pages}"
        else:
            hint = "↑↓ / WASD  navigate    Enter  cast"
        # hint is drawn during last row via the background layer — keep it simple

        return result

    def _build_row(
        self,
        y: int,
        w: int,
        page_spells: list[Spell],
        slot_pos: list[tuple[int, int]],
        ring: set[tuple[int, int]],
        spokes: set[tuple[int, int]],
        hub_x: int,
        hub_y: int,
    ) -> Text:
        # Background + ring + spoke layer (all single-width)
        bg_row: list[tuple[str, Style]] = [(" ", S_BG)] * w
        for px, py in ring:
            if py == y:
                bg_row[px] = ("·", S_RING)
        for px, py in spokes:
            if py == y:
                c = bg_row[px][0]
                if c in (" ", "·"):
                    bg_row[px] = ("·", S_SPOKE)

        # Nav hint on last visible row
        if y == self.size.height - 1:
            if self._total_pages > 1:
                hint = f" [ ] pg {self._current_page + 1}/{self._total_pages} "
            else:
                hint = " ↑↓ navigate   Enter cast "
            hx = max(0, (w - len(hint)) // 2)
            for j, ch in enumerate(hint):
                if 0 <= hx + j < w:
                    bg_row[hx + j] = (ch, S_NAV)

        # Collect overlay segments: (x_start, rich_text_of_known_width)
        overlays: list[tuple[int, Text]] = []

        if hub_y <= y < hub_y + self.HUB_H:
            overlays.append((hub_x, self._hub_row(y - hub_y)))

        for slot_i, (sx, sy) in enumerate(slot_pos):
            if sy <= y < sy + self.SLOT_H:
                global_idx = self._current_page * PAGE_SIZE + slot_i
                spell = page_spells[slot_i]
                is_active = global_idx == self.selected_index
                overlays.append((sx, self._slot_row(y - sy, spell, is_active)))

        if not overlays:
            line = Text()
            for ch, sty in bg_row:
                line.append(ch, style=sty)
            return line

        # Merge background + overlays
        overlays.sort(key=lambda o: o[0])
        line = Text()
        cursor = 0
        for x_start, seg in overlays:
            # Background up to x_start
            for i in range(cursor, min(x_start, w)):
                ch, sty = bg_row[i]
                line.append(ch, style=sty)
            line.append_text(seg)
            cursor = x_start + cell_len(str(seg))
        for i in range(cursor, w):
            ch, sty = bg_row[i]
            line.append(ch, style=sty)
        return line

    # ── Navigation ────────────────────────────────────────────────────────────

    def action_select_next(self) -> None:
        if self.spells:
            self.selected_index = (self.selected_index + 1) % len(self.spells)
            self.refresh()

    def action_select_previous(self) -> None:
        if self.spells:
            self.selected_index = (self.selected_index - 1) % len(self.spells)
            self.refresh()

    def action_next_page(self) -> None:
        if self._total_pages > 1:
            self.selected_index = ((self._current_page + 1) % self._total_pages) * PAGE_SIZE
            self.refresh()

    def action_prev_page(self) -> None:
        if self._total_pages > 1:
            self.selected_index = ((self._current_page - 1) % self._total_pages) * PAGE_SIZE
            self.refresh()

    # ── Events ────────────────────────────────────────────────────────────────

    def on_click(self, event: Click) -> None:  # type: ignore[override]
        for slot_i, (sx, sy, sw, sh) in self._slot_regions.items():
            if sx <= event.x < sx + sw and sy <= event.y < sy + sh:
                global_idx = self._current_page * PAGE_SIZE + slot_i
                self.selected_index = global_idx
                self.refresh()
                spell = self.spells[global_idx]
                if self.on_spell_selected:
                    self.on_spell_selected(spell)
                break

    def on_resize(self) -> None:  # type: ignore[override]
        self.refresh()

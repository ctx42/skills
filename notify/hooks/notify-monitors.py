#!/usr/bin/env python3
"""Show a small attention card centered on every monitor.

Used by ~/.claude/hooks/notify-project.sh. Forces the X11/XWayland backend so the
X screen spans all monitors and a small undecorated window can be move()'d onto
each one — avoiding fullscreen (which Mutter backs with an opaque black surface).
Auto-dismisses after TIMEOUT seconds, or on a click anywhere on a card.

Usage: notify-monitors.py "<message>" "<project>" [timeout_seconds]
"""
import os
import sys

# Must be set before GDK initializes so move() positions across the whole X screen.
os.environ["GDK_BACKEND"] = "x11"

import gi  # noqa: E402

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo  # noqa: E402
import cairo  # noqa: E402

message = sys.argv[1] if len(sys.argv) > 1 else "Claude needs your attention"
project = sys.argv[2] if len(sys.argv) > 2 else ""
timeout_ms = int(float(sys.argv[3]) * 1000) if len(sys.argv) > 3 else 6000

CARD_W, CARD_H = 380, 92
TOP_MARGIN = 48

display = Gdk.Display.get_default()
screen = display.get_default_screen()


def rounded_rect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -1.5708, 0)
    cr.arc(x + w - r, y + h - r, r, 0, 1.5708)
    cr.arc(x + r, y + h - r, r, 1.5708, 3.1416)
    cr.arc(x + r, y + r, r, 3.1416, 4.7124)
    cr.close_path()


def on_draw(widget, cr):
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_rgba(0, 0, 0, 0)
    cr.paint()
    cr.set_operator(cairo.OPERATOR_OVER)

    rounded_rect(cr, 1.5, 1.5, CARD_W - 3, CARD_H - 3, 14)
    cr.set_source_rgba(0.09, 0.09, 0.11, 0.96)
    cr.fill_preserve()
    cr.set_source_rgba(0.98, 0.55, 0.15, 0.98)
    cr.set_line_width(3)
    cr.stroke()

    title = f"⚠  Claude · {project}" if project else "⚠  Claude"
    layout = PangoCairo.create_layout(cr)
    layout.set_width((CARD_W - 32) * Pango.SCALE)
    layout.set_alignment(Pango.Alignment.CENTER)
    layout.set_ellipsize(Pango.EllipsizeMode.END)
    layout.set_markup(
        f"<span size='11500' weight='bold' foreground='#ffb454'>"
        f"{GLib.markup_escape_text(title)}</span>\n"
        f"<span size='9500' foreground='#e8e8e8'>"
        f"{GLib.markup_escape_text(message)}</span>",
        -1,
    )
    _, ext = layout.get_pixel_extents()
    cr.move_to(16, (CARD_H - ext.height) / 2)
    PangoCairo.show_layout(cr, layout)
    return False


def on_click(widget, event):
    # A click anywhere on any card dismisses the cards on every monitor.
    Gtk.main_quit()
    return True


def place(win, monitor_index):
    geo = display.get_monitor(monitor_index).get_geometry()
    px = geo.x + (geo.width - CARD_W) // 2
    py = geo.y + TOP_MARGIN
    win.move(px, py)


def make_card(monitor_index):
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_decorated(False)
    win.set_resizable(False)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_keep_above(True)
    win.set_accept_focus(False)
    win.set_focus_on_map(False)
    win.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
    win.set_app_paintable(True)
    win.set_default_size(CARD_W, CARD_H)
    win.set_size_request(CARD_W, CARD_H)
    visual = screen.get_rgba_visual()
    if visual is not None:
        win.set_visual(visual)
    win.connect("draw", on_draw)
    win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
    win.connect("button-press-event", on_click)
    win.move(*[0, 0])  # placeholder; real placement after show
    win.show_all()
    place(win, monitor_index)
    return win


wins = [make_card(i) for i in range(display.get_n_monitors())]
GLib.timeout_add(timeout_ms, Gtk.main_quit)
Gtk.main()

"""
MediCare – History Screen
Shows medicine-taking history with adherence statistics.
"""

from datetime import datetime, date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp

import database


class HistoryScreen(Screen):
    """Screen displaying medicine-taking history and stats."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def on_enter(self):
        self.refresh_history()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # --- Top bar ---
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(10)],
        )
        with top_bar.canvas.before:
            Color(0.13, 0.59, 0.95, 1)
            self._top_bg = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(
            pos=lambda *a: setattr(self._top_bg, "pos", top_bar.pos),
            size=lambda *a: setattr(self._top_bg, "size", top_bar.size),
        )

        title = Label(
            text="[b]Medicine History[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
        )
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        # --- Scrollable content ---
        scroll = ScrollView(do_scroll_x=False)
        with scroll.canvas.before:
            Color(0.96, 0.97, 0.98, 1)
            self._scroll_bg = Rectangle(pos=scroll.pos, size=scroll.size)
        scroll.bind(
            pos=lambda *a: setattr(self._scroll_bg, "pos", scroll.pos),
            size=lambda *a: setattr(self._scroll_bg, "size", scroll.size),
        )

        self.content_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16)],
            spacing=dp(12),
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter("height"))

        scroll.add_widget(self.content_layout)
        root.add_widget(scroll)
        self.add_widget(root)

    def refresh_history(self):
        """Reload history data."""
        self.content_layout.clear_widgets()

        # --- Adherence Stats Card ---
        stats = database.get_adherence_stats()
        self.content_layout.add_widget(self._stats_card(stats))

        self.content_layout.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # --- Date filter buttons ---
        filter_row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(38))

        self._filter_all_btn = Button(
            text="All",
            font_size=sp(13),
            background_normal="",
            background_color=(0.13, 0.59, 0.95, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        self._filter_all_btn.bind(on_release=lambda x: self._show_records("all"))

        today_btn = Button(
            text="Today",
            font_size=sp(13),
            background_normal="",
            background_color=(0.75, 0.75, 0.75, 1),
            color=(1, 1, 1, 1),
        )
        today_btn.bind(on_release=lambda x: self._show_records("today"))

        week_btn = Button(
            text="This Week",
            font_size=sp(13),
            background_normal="",
            background_color=(0.75, 0.75, 0.75, 1),
            color=(1, 1, 1, 1),
        )
        week_btn.bind(on_release=lambda x: self._show_records("week"))

        filter_row.add_widget(self._filter_all_btn)
        filter_row.add_widget(today_btn)
        filter_row.add_widget(week_btn)
        self.content_layout.add_widget(filter_row)

        # --- History Records ---
        self.records_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
        )
        self.records_layout.bind(minimum_height=self.records_layout.setter("height"))
        self.content_layout.add_widget(self.records_layout)

        self._show_records("all")

        self.content_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _show_records(self, period):
        """Show history records for the given period."""
        self.records_layout.clear_widgets()

        if period == "today":
            today_str = date.today().strftime("%Y-%m-%d")
            records = database.get_history_by_date(today_str)
        elif period == "week":
            all_records = database.get_history(limit=200)
            week_ago = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
            records = [r for r in all_records if r["scheduled_date"] >= week_ago]
        else:
            records = database.get_history(limit=100)

        self.records_layout.add_widget(self._section_title(f"📋  History ({len(records)} records)"))

        if not records:
            self.records_layout.add_widget(
                self._empty_card("No history records found.")
            )
            return

        # Group by date
        grouped = {}
        for record in records:
            d = record["scheduled_date"]
            if d not in grouped:
                grouped[d] = []
            grouped[d].append(record)

        for rec_date in sorted(grouped.keys(), reverse=True):
            # Date header
            try:
                dt = datetime.strptime(rec_date, "%Y-%m-%d")
                if rec_date == date.today().strftime("%Y-%m-%d"):
                    date_display = "Today"
                elif rec_date == (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"):
                    date_display = "Yesterday"
                else:
                    date_display = dt.strftime("%b %d, %Y")
            except ValueError:
                date_display = rec_date

            date_lbl = Label(
                text=f"[b]{date_display}[/b]",
                markup=True,
                font_size=sp(14),
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(28),
                halign="left",
            )
            date_lbl.bind(size=date_lbl.setter("text_size"))
            self.records_layout.add_widget(date_lbl)

            for record in grouped[rec_date]:
                self.records_layout.add_widget(self._history_card(record))

    def _stats_card(self, stats):
        """Create the adherence statistics card."""
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            padding=[dp(16), dp(14)],
            spacing=dp(8),
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        title = Label(
            text="[b]📊  Adherence Overview[/b]",
            markup=True,
            font_size=sp(16),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(28),
            halign="left",
        )
        title.bind(size=title.setter("text_size"))
        card.add_widget(title)

        # Stats row
        stats_row = BoxLayout(spacing=dp(8))

        # Adherence rate
        rate_color = (0.30, 0.69, 0.31, 1)
        if stats["adherence_rate"] < 50:
            rate_color = (0.96, 0.26, 0.21, 1)
        elif stats["adherence_rate"] < 80:
            rate_color = (1.0, 0.60, 0.0, 1)

        stats_row.add_widget(
            self._mini_stat("Adherence", f"{stats['adherence_rate']}%", rate_color)
        )
        stats_row.add_widget(
            self._mini_stat("Taken", str(stats["taken"]), (0.30, 0.69, 0.31, 1))
        )
        stats_row.add_widget(
            self._mini_stat("Skipped", str(stats["skipped"]), (0.96, 0.26, 0.21, 1))
        )
        stats_row.add_widget(
            self._mini_stat("Total", str(stats["total"]), (0.13, 0.59, 0.95, 1))
        )

        card.add_widget(stats_row)
        return card

    def _mini_stat(self, title, value, color):
        """Small stat widget."""
        box = BoxLayout(orientation="vertical", spacing=dp(2))

        val = Label(
            text=f"[b]{value}[/b]",
            markup=True,
            font_size=sp(20),
            color=color,
            halign="center",
            valign="bottom",
        )
        val.bind(size=val.setter("text_size"))

        lbl = Label(
            text=title,
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1),
            halign="center",
            valign="top",
        )
        lbl.bind(size=lbl.setter("text_size"))

        box.add_widget(val)
        box.add_widget(lbl)
        return box

    def _history_card(self, record):
        """Create a history record card."""
        is_taken = record["action"] == "taken"

        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[dp(14), dp(10)],
            spacing=dp(12),
        )
        bg_color = (0.94, 0.97, 0.94, 1) if is_taken else (0.98, 0.94, 0.94, 1)
        with card.canvas.before:
            Color(*bg_color)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        # Status icon
        icon = Label(
            text="✅" if is_taken else "⏭️",
            font_size=sp(20),
            size_hint_x=None,
            width=dp(32),
        )
        card.add_widget(icon)

        # Info
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        name_lbl = Label(
            text=f"[b]{record['medicine_name']}[/b]  •  {record['dosage']}",
            markup=True,
            font_size=sp(14),
            color=(0.13, 0.13, 0.13, 1),
            halign="left",
            valign="bottom",
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        time_text = self._format_time(record["scheduled_time"])
        action_text = "Taken" if is_taken else "Skipped"
        detail_lbl = Label(
            text=f"{action_text} at {time_text}",
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign="left",
            valign="top",
        )
        detail_lbl.bind(size=detail_lbl.setter("text_size"))

        info.add_widget(name_lbl)
        info.add_widget(detail_lbl)
        card.add_widget(info)

        return card

    def _section_title(self, text):
        lbl = Label(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size=sp(16),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(30),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _empty_card(self, text):
        card = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(16), dp(12)])
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )
        lbl = Label(
            text=text,
            font_size=sp(14),
            color=(0.6, 0.6, 0.6, 1),
            halign="center",
            valign="center",
        )
        lbl.bind(size=lbl.setter("text_size"))
        card.add_widget(lbl)
        return card

    def _format_time(self, time_str):
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.strftime("%I:%M %p")
        except (ValueError, TypeError):
            return time_str

"""
MediCare – Home Screen
Dashboard showing today's schedule, upcoming reminders, and stats.
"""

from datetime import datetime, date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock

import database


class HomeScreen(Screen):
    """Main dashboard screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def on_enter(self):
        self.refresh_data()

    def _build_ui(self):
        # Root layout
        root = BoxLayout(orientation="vertical")

        # --- Top bar ---
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(10)],
        )
        with top_bar.canvas.before:
            Color(0.13, 0.59, 0.95, 1)  # #2196F3
            self._top_bg = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(
            pos=lambda *a: setattr(self._top_bg, "pos", top_bar.pos),
            size=lambda *a: setattr(self._top_bg, "size", top_bar.size),
        )

        app_title = Label(
            text="[b]MediCare[/b]",
            markup=True,
            font_size=sp(22),
            color=(1, 1, 1, 1),
            halign="left",
            valign="center",
            size_hint_x=0.6,
        )
        app_title.bind(size=app_title.setter("text_size"))

        self.date_label = Label(
            text=datetime.now().strftime("%b %d, %Y"),
            font_size=sp(14),
            color=(1, 1, 1, 0.9),
            halign="right",
            valign="center",
            size_hint_x=0.4,
        )
        self.date_label.bind(size=self.date_label.setter("text_size"))

        top_bar.add_widget(app_title)
        top_bar.add_widget(self.date_label)
        root.add_widget(top_bar)

        # --- Scrollable body ---
        scroll = ScrollView(do_scroll_x=False)
        self.body = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16)],
            spacing=dp(14),
        )
        self.body.bind(minimum_height=self.body.setter("height"))

        # Background color
        with scroll.canvas.before:
            Color(0.96, 0.97, 0.98, 1)  # #F5F7FA
            self._body_bg = Rectangle(pos=scroll.pos, size=scroll.size)
        scroll.bind(
            pos=lambda *a: setattr(self._body_bg, "pos", scroll.pos),
            size=lambda *a: setattr(self._body_bg, "size", scroll.size),
        )

        scroll.add_widget(self.body)
        root.add_widget(scroll)

        self.add_widget(root)

    def refresh_data(self):
        """Refresh dashboard data."""
        self.date_label.text = datetime.now().strftime("%b %d, %Y")
        self.body.clear_widgets()

        # Greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning! ☀️"
        elif hour < 17:
            greeting = "Good Afternoon! 🌤️"
        else:
            greeting = "Good Evening! 🌙"

        greet_label = Label(
            text=f"[b]{greeting}[/b]",
            markup=True,
            font_size=sp(20),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(36),
            halign="left",
        )
        greet_label.bind(size=greet_label.setter("text_size"))
        self.body.add_widget(greet_label)

        subtitle = Label(
            text="Here's your medicine schedule for today",
            font_size=sp(14),
            color=(0.46, 0.46, 0.46, 1),
            size_hint_y=None,
            height=dp(22),
            halign="left",
        )
        subtitle.bind(size=subtitle.setter("text_size"))
        self.body.add_widget(subtitle)

        self.body.add_widget(Widget(size_hint_y=None, height=dp(6)))

        # --- Stats Cards ---
        stats_row = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(100))

        total_count = database.get_medicine_count()
        todays_meds = database.get_todays_medicines()
        upcoming = database.get_upcoming_medicines(limit=10)
        stats_data = database.get_adherence_stats()

        stats_row.add_widget(
            self._stat_card("Total\nMedicines", str(total_count), (0.13, 0.59, 0.95, 1))
        )
        stats_row.add_widget(
            self._stat_card("Today's\nSchedule", str(len(todays_meds)), (0.30, 0.69, 0.31, 1))
        )
        stats_row.add_widget(
            self._stat_card("Adherence\nRate", f"{stats_data['adherence_rate']}%", (1.0, 0.60, 0.0, 1))
        )

        self.body.add_widget(stats_row)

        # --- Upcoming Reminders ---
        self.body.add_widget(Widget(size_hint_y=None, height=dp(4)))
        self.body.add_widget(self._section_title("⏰  Upcoming Reminders"))

        if upcoming:
            for med in upcoming[:4]:
                self.body.add_widget(self._medicine_card(med, upcoming=True))
        else:
            self.body.add_widget(self._empty_card("No upcoming reminders. You're all caught up! ✅"))

        # --- Today's Full Schedule ---
        self.body.add_widget(Widget(size_hint_y=None, height=dp(4)))
        self.body.add_widget(self._section_title("📋  Today's Schedule"))

        if todays_meds:
            today_str = date.today().strftime("%Y-%m-%d")
            for med in todays_meds:
                handled = database.is_medicine_handled_today(med["id"], today_str)
                self.body.add_widget(self._medicine_card(med, done=handled))
        else:
            self.body.add_widget(self._empty_card("No medicines scheduled for today."))

        # Bottom padding
        self.body.add_widget(Widget(size_hint_y=None, height=dp(16)))

    def _stat_card(self, title, value, color):
        """Create a statistics card widget."""
        card = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(4))
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        val_label = Label(
            text=f"[b]{value}[/b]",
            markup=True,
            font_size=sp(24),
            color=color,
            halign="center",
            valign="bottom",
            size_hint_y=0.5,
        )
        val_label.bind(size=val_label.setter("text_size"))

        title_label = Label(
            text=title,
            font_size=sp(11),
            color=(0.46, 0.46, 0.46, 1),
            halign="center",
            valign="top",
            size_hint_y=0.5,
        )
        title_label.bind(size=title_label.setter("text_size"))

        card.add_widget(val_label)
        card.add_widget(title_label)
        return card

    def _section_title(self, text):
        """Create a section title."""
        lbl = Label(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size=sp(17),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(32),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _medicine_card(self, med, upcoming=False, done=False):
        """Create a medicine info card."""
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=[dp(16), dp(12)],
            spacing=dp(12),
        )
        with card.canvas.before:
            if done:
                Color(0.94, 0.97, 0.94, 1)  # Light green
            else:
                Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        # Left: Colored time badge
        time_box = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(60),
        )
        time_text = self._format_time(med["reminder_time"])
        time_lbl = Label(
            text=f"[b]{time_text}[/b]",
            markup=True,
            font_size=sp(13),
            color=(0.13, 0.59, 0.95, 1),
            halign="center",
            valign="center",
        )
        time_lbl.bind(size=time_lbl.setter("text_size"))
        time_box.add_widget(time_lbl)
        card.add_widget(time_box)

        # Center: Medicine info
        info_box = BoxLayout(orientation="vertical", spacing=dp(2))
        name_lbl = Label(
            text=f"[b]{med['name']}[/b]",
            markup=True,
            font_size=sp(16),
            color=(0.13, 0.13, 0.13, 1),
            halign="left",
            valign="bottom",
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        dosage_lbl = Label(
            text=med["dosage"],
            font_size=sp(13),
            color=(0.46, 0.46, 0.46, 1),
            halign="left",
            valign="top",
        )
        dosage_lbl.bind(size=dosage_lbl.setter("text_size"))

        info_box.add_widget(name_lbl)
        info_box.add_widget(dosage_lbl)
        card.add_widget(info_box)

        # Right: Status indicator
        if done:
            status = Label(
                text="✅",
                font_size=sp(20),
                size_hint_x=None,
                width=dp(40),
                halign="center",
            )
            card.add_widget(status)
        elif upcoming:
            status = Label(
                text="🔔",
                font_size=sp(18),
                size_hint_x=None,
                width=dp(40),
                halign="center",
            )
            card.add_widget(status)

        return card

    def _empty_card(self, text):
        """Create a placeholder card."""
        card = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(12)],
        )
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
        """Format HH:MM to 12-hour format."""
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.strftime("%I:%M\n%p")
        except (ValueError, TypeError):
            return time_str

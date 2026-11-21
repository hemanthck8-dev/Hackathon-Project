"""
MediCare – Reminder System
Checks for due medicines and shows reminder popups.
"""

from datetime import datetime, date
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp

import database


class ReminderPopup(ModalView):
    """A styled popup for medicine reminders."""

    def __init__(self, medicine, callback, **kwargs):
        super().__init__(**kwargs)
        self.medicine = medicine
        self.callback = callback
        self.size_hint = (0.85, None)
        self.height = dp(320)
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        self.auto_dismiss = False

        # Main container
        container = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))
        with container.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = RoundedRectangle(
                pos=container.pos, size=container.size, radius=[dp(20)]
            )
        container.bind(
            pos=lambda *a: setattr(self._bg_rect, "pos", container.pos),
            size=lambda *a: setattr(self._bg_rect, "size", container.size),
        )

        # Icon / Header
        header = Label(
            text="[b]⏰  Medicine Reminder[/b]",
            markup=True,
            font_size=sp(20),
            color=(0.13, 0.59, 0.95, 1),
            size_hint_y=None,
            height=dp(36),
        )
        container.add_widget(header)

        # Divider
        divider = BoxLayout(size_hint_y=None, height=dp(2))
        with divider.canvas.before:
            Color(0.91, 0.93, 0.96, 1)
            self._div_rect = RoundedRectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda *a: setattr(self._div_rect, "pos", divider.pos),
            size=lambda *a: setattr(self._div_rect, "size", divider.size),
        )
        container.add_widget(divider)

        # Medicine info
        name_label = Label(
            text=f"[b]{medicine['name']}[/b]",
            markup=True,
            font_size=sp(22),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(34),
        )
        container.add_widget(name_label)

        dosage_label = Label(
            text=f"Dosage: {medicine['dosage']}",
            font_size=sp(16),
            color=(0.46, 0.46, 0.46, 1),
            size_hint_y=None,
            height=dp(26),
        )
        container.add_widget(dosage_label)

        time_label = Label(
            text=f"Scheduled: {self._format_time(medicine['reminder_time'])}",
            font_size=sp(15),
            color=(0.46, 0.46, 0.46, 1),
            size_hint_y=None,
            height=dp(26),
        )
        container.add_widget(time_label)

        if medicine.get("notes"):
            notes_label = Label(
                text=f"Note: {medicine['notes']}",
                font_size=sp(13),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(22),
            )
            container.add_widget(notes_label)

        # Spacer
        container.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))

        # Buttons
        btn_row = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(48))

        skip_btn = Button(
            text="Skip",
            font_size=sp(16),
            background_normal="",
            background_color=(0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        skip_btn.bind(on_release=lambda x: self._on_action("skipped"))

        taken_btn = Button(
            text="✓  Taken",
            font_size=sp(16),
            background_normal="",
            background_color=(0.30, 0.69, 0.31, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        taken_btn.bind(on_release=lambda x: self._on_action("taken"))

        btn_row.add_widget(skip_btn)
        btn_row.add_widget(taken_btn)
        container.add_widget(btn_row)

        self.add_widget(container)

    def _format_time(self, time_str):
        """Format HH:MM to 12-hour format."""
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.strftime("%I:%M %p")
        except (ValueError, TypeError):
            return time_str

    def _on_action(self, action):
        """Handle taken or skipped."""
        med = self.medicine
        database.record_action(
            med["id"], med["name"], med["dosage"], med["reminder_time"], action
        )
        self.dismiss()
        if self.callback:
            self.callback(med["id"], action)


class ReminderManager:
    """Manages checking and displaying medicine reminders."""

    def __init__(self, app=None):
        self.app = app
        self._shown_reminders = set()  # (medicine_id, date_str) pairs already shown
        self._active_popup = None
        self._pending_queue = []
        self._check_event = None

    def start(self):
        """Start the reminder checking loop (every 30 seconds)."""
        if self._check_event:
            self._check_event.cancel()
        self._check_event = Clock.schedule_interval(self._check_reminders, 30)
        # Also run an immediate check after a short delay
        Clock.schedule_once(lambda dt: self._check_reminders(0), 2)

    def stop(self):
        """Stop the reminder checking loop."""
        if self._check_event:
            self._check_event.cancel()
            self._check_event = None

    def _check_reminders(self, dt):
        """Check for due medicines and queue reminders."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today_str = date.today().strftime("%Y-%m-%d")

        todays_meds = database.get_todays_medicines()

        for med in todays_meds:
            med_time = med["reminder_time"]
            key = (med["id"], today_str)

            # Skip if already shown today
            if key in self._shown_reminders:
                continue

            # Skip if already handled in database
            if database.is_medicine_handled_today(med["id"], today_str):
                self._shown_reminders.add(key)
                continue

            # Check if the medicine is due (within a 5-minute window)
            if self._is_time_due(med_time, current_time):
                self._shown_reminders.add(key)
                self._pending_queue.append(med)

        # Show next popup if none is active
        self._show_next_popup()

    def _is_time_due(self, scheduled_time, current_time):
        """Check if scheduled_time is due (current time is within 0-5 min after)."""
        try:
            sched = datetime.strptime(scheduled_time, "%H:%M")
            curr = datetime.strptime(current_time, "%H:%M")
            diff = (curr - sched).total_seconds() / 60
            return 0 <= diff <= 5
        except (ValueError, TypeError):
            return False

    def _show_next_popup(self):
        """Show the next pending reminder popup."""
        if self._active_popup or not self._pending_queue:
            return

        med = self._pending_queue.pop(0)
        self._active_popup = ReminderPopup(
            medicine=med, callback=self._on_popup_closed
        )
        self._active_popup.open()

    def _on_popup_closed(self, med_id, action):
        """Callback when a reminder popup is closed."""
        self._active_popup = None
        # Refresh home screen if visible
        if self.app:
            try:
                sm = self.app.root
                if sm and hasattr(sm, "current") and sm.current == "home":
                    screen = sm.get_screen("home")
                    if hasattr(screen, "refresh_data"):
                        screen.refresh_data()
            except Exception:
                pass
        # Show next queued popup
        Clock.schedule_once(lambda dt: self._show_next_popup(), 0.5)

    def reset_daily(self):
        """Reset shown reminders (call at midnight or app start for a new day)."""
        self._shown_reminders.clear()
        self._pending_queue.clear()

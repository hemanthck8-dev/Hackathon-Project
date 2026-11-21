"""
MediCare – Add Medicine Screen
Form for adding and editing medicines.
"""

from datetime import datetime, date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp

import database


class AddMedicineScreen(Screen):
    """Screen for adding or editing a medicine."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editing_id = None
        self._build_ui()

    def on_enter(self):
        """Called when screen is shown. Reset if not editing."""
        if not self.editing_id:
            self._clear_form()

    def load_medicine(self, med_id):
        """Load an existing medicine for editing."""
        med = database.get_medicine_by_id(med_id)
        if not med:
            return

        self.editing_id = med_id
        self.title_label.text = "[b]Edit Medicine[/b]"
        self.name_input.text = med["name"]
        self.dosage_input.text = med["dosage"]

        # Parse time
        self.hour_spinner.text = med["reminder_time"].split(":")[0] if ":" in med["reminder_time"] else "08"
        self.minute_spinner.text = med["reminder_time"].split(":")[1] if ":" in med["reminder_time"] else "00"

        self.start_input.text = med.get("start_date", "")
        self.end_input.text = med.get("end_date", "")
        self.notes_input.text = med.get("notes", "")

        # Set frequency
        freq = med.get("frequency", "daily").lower()
        if freq == "daily":
            self.freq_daily.state = "down"
            self.freq_custom.state = "normal"
            self._hide_day_buttons()
        else:
            self.freq_daily.state = "normal"
            self.freq_custom.state = "down"
            self._show_day_buttons()
            selected = [d.strip().lower() for d in freq.split(",")]
            for btn in self.day_buttons:
                if btn.text.lower() in selected:
                    btn.state = "down"
                else:
                    btn.state = "normal"

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # --- Top bar ---
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(10)],
        )
        with top_bar.canvas.before:
            Color(0.13, 0.59, 0.95, 1)
            self._top_bg = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(
            pos=lambda *a: setattr(self._top_bg, "pos", top_bar.pos),
            size=lambda *a: setattr(self._top_bg, "size", top_bar.size),
        )

        back_btn = Button(
            text="← Back",
            font_size=sp(15),
            size_hint_x=None,
            width=dp(80),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
        )
        back_btn.bind(on_release=lambda x: self._go_back())

        self.title_label = Label(
            text="[b]Add Medicine[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
        )

        # Spacer to balance back button
        spacer = Widget(size_hint_x=None, width=dp(80))

        top_bar.add_widget(back_btn)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(spacer)
        root.add_widget(top_bar)

        # --- Scrollable form ---
        scroll = ScrollView(do_scroll_x=False)
        with scroll.canvas.before:
            Color(0.96, 0.97, 0.98, 1)
            self._scroll_bg = Rectangle(pos=scroll.pos, size=scroll.size)
        scroll.bind(
            pos=lambda *a: setattr(self._scroll_bg, "pos", scroll.pos),
            size=lambda *a: setattr(self._scroll_bg, "size", scroll.size),
        )

        form = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(20), dp(20)],
            spacing=dp(16),
        )
        form.bind(minimum_height=form.setter("height"))

        # -- Medicine Name --
        form.add_widget(self._field_label("Medicine Name *"))
        self.name_input = self._styled_input("Enter medicine name")
        form.add_widget(self.name_input)

        # -- Dosage --
        form.add_widget(self._field_label("Dosage *"))
        self.dosage_input = self._styled_input("e.g., 1 tablet, 5 ml, 500 mg")
        form.add_widget(self.dosage_input)

        # -- Reminder Time --
        form.add_widget(self._field_label("Reminder Time *"))
        time_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))

        self.hour_spinner = Spinner(
            text="08",
            values=[f"{h:02d}" for h in range(0, 24)],
            font_size=sp(16),
            background_normal="",
            background_color=(1, 1, 1, 1),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_x=0.4,
        )

        colon_label = Label(
            text=":",
            font_size=sp(24),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_x=0.1,
            bold=True,
        )

        self.minute_spinner = Spinner(
            text="00",
            values=[f"{m:02d}" for m in range(0, 60, 5)],
            font_size=sp(16),
            background_normal="",
            background_color=(1, 1, 1, 1),
            color=(0.13, 0.13, 0.13, 1),
            size_hint_x=0.4,
        )

        time_hint = Label(
            text="(24h)",
            font_size=sp(12),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=0.2,
        )

        time_row.add_widget(self.hour_spinner)
        time_row.add_widget(colon_label)
        time_row.add_widget(self.minute_spinner)
        time_row.add_widget(time_hint)
        form.add_widget(time_row)

        # -- Start Date --
        form.add_widget(self._field_label("Start Date *  (YYYY-MM-DD)"))
        self.start_input = self._styled_input("e.g., 2026-11-21")
        self.start_input.text = date.today().strftime("%Y-%m-%d")
        form.add_widget(self.start_input)

        # -- End Date --
        form.add_widget(self._field_label("End Date  (YYYY-MM-DD, optional)"))
        self.end_input = self._styled_input("Leave empty for ongoing")
        form.add_widget(self.end_input)

        # -- Frequency --
        form.add_widget(self._field_label("Frequency"))
        freq_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))

        self.freq_daily = ToggleButton(
            text="Daily",
            group="freq",
            state="down",
            font_size=sp(14),
            background_normal="",
            background_color=(0.85, 0.85, 0.85, 1),
            background_down="",
            color=(1, 1, 1, 1),
        )
        self.freq_daily.bind(state=self._on_freq_change)

        self.freq_custom = ToggleButton(
            text="Custom Days",
            group="freq",
            font_size=sp(14),
            background_normal="",
            background_color=(0.85, 0.85, 0.85, 1),
            background_down="",
            color=(1, 1, 1, 1),
        )
        self.freq_custom.bind(state=self._on_freq_change)

        freq_row.add_widget(self.freq_daily)
        freq_row.add_widget(self.freq_custom)
        form.add_widget(freq_row)

        # -- Day selection (hidden by default) --
        self.days_container = BoxLayout(
            orientation="vertical", size_hint_y=None, height=0, opacity=0
        )
        days_grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(90))
        self.day_buttons = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            btn = ToggleButton(
                text=day[:3],
                font_size=sp(13),
                size_hint_y=None,
                height=dp(38),
                background_normal="",
                background_color=(0.85, 0.85, 0.85, 1),
                background_down="",
                color=(1, 1, 1, 1),
            )
            btn._full_day = day
            days_grid.add_widget(btn)
            self.day_buttons.append(btn)

        self.days_container.add_widget(days_grid)
        form.add_widget(self.days_container)

        # -- Notes --
        form.add_widget(self._field_label("Notes (optional)"))
        self.notes_input = TextInput(
            hint_text="Any additional notes...",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
            font_size=sp(15),
            padding=[dp(14), dp(10)],
            background_normal="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.13, 0.13, 0.13, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1),
            cursor_color=(0.13, 0.59, 0.95, 1),
        )
        form.add_widget(self.notes_input)

        form.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # -- Save Button --
        save_btn = Button(
            text="💾  Save Medicine",
            font_size=sp(17),
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.13, 0.59, 0.95, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        save_btn.bind(on_release=lambda x: self._save_medicine())
        form.add_widget(save_btn)

        form.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    def _field_label(self, text):
        lbl = Label(
            text=text,
            font_size=sp(14),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(24),
            halign="left",
            bold=True,
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _styled_input(self, hint):
        inp = TextInput(
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(46),
            font_size=sp(15),
            padding=[dp(14), dp(12)],
            background_normal="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.13, 0.13, 0.13, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1),
            cursor_color=(0.13, 0.59, 0.95, 1),
        )
        return inp

    def _on_freq_change(self, instance, value):
        if self.freq_custom.state == "down":
            self._show_day_buttons()
            # Style toggles
            self.freq_custom.background_color = (0.13, 0.59, 0.95, 1)
            self.freq_daily.background_color = (0.85, 0.85, 0.85, 1)
        else:
            self._hide_day_buttons()
            self.freq_daily.background_color = (0.13, 0.59, 0.95, 1)
            self.freq_custom.background_color = (0.85, 0.85, 0.85, 1)

    def _show_day_buttons(self):
        self.days_container.height = dp(100)
        self.days_container.opacity = 1

    def _hide_day_buttons(self):
        self.days_container.height = 0
        self.days_container.opacity = 0

    def _clear_form(self):
        """Reset the form to defaults."""
        self.editing_id = None
        self.title_label.text = "[b]Add Medicine[/b]"
        self.name_input.text = ""
        self.dosage_input.text = ""
        self.hour_spinner.text = "08"
        self.minute_spinner.text = "00"
        self.start_input.text = date.today().strftime("%Y-%m-%d")
        self.end_input.text = ""
        self.notes_input.text = ""
        self.freq_daily.state = "down"
        self.freq_custom.state = "normal"
        self.freq_daily.background_color = (0.13, 0.59, 0.95, 1)
        self.freq_custom.background_color = (0.85, 0.85, 0.85, 1)
        self._hide_day_buttons()
        for btn in self.day_buttons:
            btn.state = "normal"

    def _validate(self):
        """Validate form input. Returns error message or None."""
        name = self.name_input.text.strip()
        dosage = self.dosage_input.text.strip()
        start = self.start_input.text.strip()

        if not name:
            return "Medicine name is required."
        if not dosage:
            return "Dosage is required."
        if not start:
            return "Start date is required."

        # Validate date format
        try:
            datetime.strptime(start, "%Y-%m-%d")
        except ValueError:
            return "Start date must be in YYYY-MM-DD format."

        end = self.end_input.text.strip()
        if end:
            try:
                datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                return "End date must be in YYYY-MM-DD format."

        # Custom frequency must have at least one day
        if self.freq_custom.state == "down":
            selected = [b for b in self.day_buttons if b.state == "down"]
            if not selected:
                return "Select at least one day for custom frequency."

        return None

    def _save_medicine(self):
        """Save or update the medicine."""
        error = self._validate()
        if error:
            self._show_message("Validation Error", error)
            return

        name = self.name_input.text.strip()
        dosage = self.dosage_input.text.strip()
        reminder_time = f"{self.hour_spinner.text}:{self.minute_spinner.text}"
        start_date = self.start_input.text.strip()
        end_date = self.end_input.text.strip()
        notes = self.notes_input.text.strip()

        if self.freq_daily.state == "down":
            frequency = "daily"
        else:
            selected = [b._full_day.lower() for b in self.day_buttons if b.state == "down"]
            frequency = ",".join(selected)

        if self.editing_id:
            database.update_medicine(
                self.editing_id, name, dosage, reminder_time,
                start_date, end_date, frequency, notes
            )
            msg = f"{name} has been updated successfully!"
        else:
            database.add_medicine(
                name, dosage, reminder_time,
                start_date, end_date, frequency, notes
            )
            msg = f"{name} has been added successfully!"

        self._show_message("Success ✅", msg, success=True)
        self._clear_form()

    def _show_message(self, title, message, success=False):
        """Show a styled popup message."""
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        msg_label = Label(
            text=message,
            font_size=sp(15),
            color=(0.13, 0.13, 0.13, 1),
            halign="center",
            valign="center",
            size_hint_y=0.6,
        )
        msg_label.bind(size=msg_label.setter("text_size"))

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.3),
            separator_color=(0.13, 0.59, 0.95, 1) if success else (0.96, 0.26, 0.21, 1),
        )

        ok_btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(42),
            font_size=sp(15),
            background_normal="",
            background_color=(0.13, 0.59, 0.95, 1) if success else (0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
        )
        ok_btn.bind(on_release=popup.dismiss)

        content.add_widget(msg_label)
        content.add_widget(ok_btn)
        popup.open()

    def _go_back(self):
        """Navigate back to medicines screen."""
        self._clear_form()
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "medicines"

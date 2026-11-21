"""
MediCare – Medicines Screen
Displays all saved medicines with edit and delete functionality.
"""

from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp

import database


class MedicinesScreen(Screen):
    """Screen displaying all saved medicines."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def on_enter(self):
        self.refresh_list()

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
            text="[b]My Medicines[/b]",
            markup=True,
            font_size=sp(20),
            color=(1, 1, 1, 1),
        )
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        # --- Scrollable list ---
        scroll = ScrollView(do_scroll_x=False)
        with scroll.canvas.before:
            Color(0.96, 0.97, 0.98, 1)
            self._scroll_bg = Rectangle(pos=scroll.pos, size=scroll.size)
        scroll.bind(
            pos=lambda *a: setattr(self._scroll_bg, "pos", scroll.pos),
            size=lambda *a: setattr(self._scroll_bg, "size", scroll.size),
        )

        self.list_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16)],
            spacing=dp(12),
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)

        # --- Floating Add Button ---
        add_btn_container = BoxLayout(
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={"right": 0.95, "y": 0.1},
        )
        add_btn = Button(
            text="+",
            font_size=sp(28),
            bold=True,
            background_normal="",
            background_color=(0.13, 0.59, 0.95, 1),
            color=(1, 1, 1, 1),
        )
        add_btn.bind(on_release=lambda x: self._go_add())
        add_btn_container.add_widget(add_btn)

        from kivy.uix.floatlayout import FloatLayout
        float_root = FloatLayout()
        float_root.add_widget(root)
        float_root.add_widget(add_btn_container)

        self.add_widget(float_root)

    def refresh_list(self):
        """Reload medicines from database."""
        self.list_layout.clear_widgets()

        medicines = database.get_all_medicines()

        if not medicines:
            self.list_layout.add_widget(Widget(size_hint_y=None, height=dp(40)))
            empty = Label(
                text="No medicines added yet.\nTap + to add your first medicine.",
                font_size=sp(16),
                color=(0.5, 0.5, 0.5, 1),
                halign="center",
                valign="center",
                size_hint_y=None,
                height=dp(80),
            )
            empty.bind(size=empty.setter("text_size"))
            self.list_layout.add_widget(empty)
            return

        # Group by time period
        morning = []
        afternoon = []
        evening = []
        night = []

        for med in medicines:
            try:
                hour = int(med["reminder_time"].split(":")[0])
            except (ValueError, IndexError):
                hour = 12

            if hour < 12:
                morning.append(med)
            elif hour < 17:
                afternoon.append(med)
            elif hour < 21:
                evening.append(med)
            else:
                night.append(med)

        groups = [
            ("🌅  Morning", morning),
            ("☀️  Afternoon", afternoon),
            ("🌆  Evening", evening),
            ("🌙  Night", night),
        ]

        for label, meds in groups:
            if meds:
                self.list_layout.add_widget(self._section_label(label))
                for med in meds:
                    self.list_layout.add_widget(self._medicine_card(med))

        self.list_layout.add_widget(Widget(size_hint_y=None, height=dp(80)))

    def _section_label(self, text):
        lbl = Label(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size=sp(15),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(30),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _medicine_card(self, med):
        """Create a detailed medicine card with edit/delete."""
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=[dp(16), dp(12)],
            spacing=dp(6),
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        # Top row: Name + Time
        top_row = BoxLayout(size_hint_y=None, height=dp(28))
        name_lbl = Label(
            text=f"[b]{med['name']}[/b]",
            markup=True,
            font_size=sp(17),
            color=(0.13, 0.13, 0.13, 1),
            halign="left",
            valign="center",
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        time_text = self._format_time(med["reminder_time"])
        time_lbl = Label(
            text=time_text,
            font_size=sp(14),
            color=(0.13, 0.59, 0.95, 1),
            halign="right",
            valign="center",
            size_hint_x=None,
            width=dp(80),
            bold=True,
        )
        time_lbl.bind(size=time_lbl.setter("text_size"))

        top_row.add_widget(name_lbl)
        top_row.add_widget(time_lbl)
        card.add_widget(top_row)

        # Details row
        dosage_lbl = Label(
            text=f"Dosage: {med['dosage']}",
            font_size=sp(13),
            color=(0.46, 0.46, 0.46, 1),
            halign="left",
            size_hint_y=None,
            height=dp(20),
        )
        dosage_lbl.bind(size=dosage_lbl.setter("text_size"))
        card.add_widget(dosage_lbl)

        freq = med.get("frequency", "daily")
        freq_display = "Daily" if freq.lower() == "daily" else freq.title()
        freq_lbl = Label(
            text=f"Frequency: {freq_display}",
            font_size=sp(12),
            color=(0.55, 0.55, 0.55, 1),
            halign="left",
            size_hint_y=None,
            height=dp(18),
        )
        freq_lbl.bind(size=freq_lbl.setter("text_size"))
        card.add_widget(freq_lbl)

        if med.get("notes"):
            notes_lbl = Label(
                text=f"Note: {med['notes']}",
                font_size=sp(11),
                color=(0.6, 0.6, 0.6, 1),
                halign="left",
                size_hint_y=None,
                height=dp(16),
            )
            notes_lbl.bind(size=notes_lbl.setter("text_size"))
            card.add_widget(notes_lbl)

        # Action buttons
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(36))

        edit_btn = Button(
            text="✏️ Edit",
            font_size=sp(13),
            background_normal="",
            background_color=(1.0, 0.60, 0.0, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        med_id = med["id"]
        edit_btn.bind(on_release=lambda x, mid=med_id: self._edit_medicine(mid))

        del_btn = Button(
            text="🗑️ Delete",
            font_size=sp(13),
            background_normal="",
            background_color=(0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        del_btn.bind(on_release=lambda x, mid=med_id, nm=med["name"]: self._confirm_delete(mid, nm))

        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        card.add_widget(btn_row)

        return card

    def _edit_medicine(self, med_id):
        """Navigate to add screen in edit mode."""
        if self.manager:
            add_screen = self.manager.get_screen("add_medicine")
            add_screen.load_medicine(med_id)
            self.manager.transition.direction = "left"
            self.manager.current = "add_medicine"

    def _confirm_delete(self, med_id, med_name):
        """Show delete confirmation popup."""
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        msg = Label(
            text=f"Are you sure you want to delete\n[b]{med_name}[/b]?",
            markup=True,
            font_size=sp(15),
            color=(0.13, 0.13, 0.13, 1),
            halign="center",
            valign="center",
            size_hint_y=0.5,
        )
        msg.bind(size=msg.setter("text_size"))

        popup = Popup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.8, 0.3),
            separator_color=(0.96, 0.26, 0.21, 1),
        )

        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(42))

        cancel_btn = Button(
            text="Cancel",
            font_size=sp(14),
            background_normal="",
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1),
        )
        cancel_btn.bind(on_release=popup.dismiss)

        delete_btn = Button(
            text="Delete",
            font_size=sp(14),
            background_normal="",
            background_color=(0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )

        def do_delete(x):
            database.delete_medicine(med_id)
            popup.dismiss()
            self.refresh_list()

        delete_btn.bind(on_release=do_delete)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(delete_btn)

        content.add_widget(msg)
        content.add_widget(btn_row)
        popup.open()

    def _go_add(self):
        """Navigate to add medicine screen."""
        if self.manager:
            add_screen = self.manager.get_screen("add_medicine")
            add_screen._clear_form()
            self.manager.transition.direction = "left"
            self.manager.current = "add_medicine"

    def _format_time(self, time_str):
        """Format HH:MM to 12-hour format."""
        try:
            t = datetime.strptime(time_str, "%H:%M")
            return t.strftime("%I:%M %p")
        except (ValueError, TypeError):
            return time_str

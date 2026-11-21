"""
MediCare – Settings Screen
Notification preferences and app information.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp

import database


class SettingsScreen(Screen):
    """Settings screen with notification preferences and app info."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def on_enter(self):
        self._load_settings()

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
            text="[b]Settings[/b]",
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

        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(20)],
            spacing=dp(14),
        )
        content.bind(minimum_height=content.setter("height"))

        # --- Notification Settings ---
        content.add_widget(self._section_title("🔔  Notification Preferences"))

        self.notif_switch = Switch(active=True)
        content.add_widget(
            self._setting_row("Enable Reminders", "Get medicine reminders", self.notif_switch)
        )
        self.notif_switch.bind(active=lambda inst, val: database.set_setting("notifications_enabled", "1" if val else "0"))

        self.sound_switch = Switch(active=True)
        content.add_widget(
            self._setting_row("Reminder Sound", "Play sound with reminders", self.sound_switch)
        )
        self.sound_switch.bind(active=lambda inst, val: database.set_setting("reminder_sound", "1" if val else "0"))

        self.vibrate_switch = Switch(active=True)
        content.add_widget(
            self._setting_row("Vibration", "Vibrate on reminders", self.vibrate_switch)
        )
        self.vibrate_switch.bind(active=lambda inst, val: database.set_setting("reminder_vibrate", "1" if val else "0"))

        content.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # --- Data Management ---
        content.add_widget(self._section_title("🗄️  Data Management"))

        clear_history_btn = Button(
            text="🗑️  Clear History",
            font_size=sp(15),
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=(0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        clear_history_btn.bind(on_release=lambda x: self._confirm_clear_history())
        content.add_widget(clear_history_btn)

        content.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # --- About ---
        content.add_widget(self._section_title("ℹ️  About"))
        content.add_widget(self._about_card())

        content.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _load_settings(self):
        """Load current settings from database."""
        self.notif_switch.active = database.get_setting("notifications_enabled", "1") == "1"
        self.sound_switch.active = database.get_setting("reminder_sound", "1") == "1"
        self.vibrate_switch.active = database.get_setting("reminder_vibrate", "1") == "1"

    def _section_title(self, text):
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

    def _setting_row(self, title, subtitle, switch_widget):
        """Create a setting row with label and switch."""
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(70),
            padding=[dp(16), dp(12)],
            spacing=dp(10),
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        # Text side
        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        title_lbl = Label(
            text=f"[b]{title}[/b]",
            markup=True,
            font_size=sp(15),
            color=(0.13, 0.13, 0.13, 1),
            halign="left",
            valign="bottom",
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))

        sub_lbl = Label(
            text=subtitle,
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign="left",
            valign="top",
        )
        sub_lbl.bind(size=sub_lbl.setter("text_size"))

        text_box.add_widget(title_lbl)
        text_box.add_widget(sub_lbl)
        card.add_widget(text_box)

        # Switch
        switch_container = BoxLayout(size_hint_x=None, width=dp(60))
        switch_container.add_widget(switch_widget)
        card.add_widget(switch_container)

        return card

    def _about_card(self):
        """Create the about information card."""
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=[dp(20), dp(16)],
            spacing=dp(8),
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(
            pos=lambda *a, r=r, c=card: setattr(r, "pos", c.pos),
            size=lambda *a, r=r, c=card: setattr(r, "size", c.size),
        )

        app_name = Label(
            text="[b]MediCare[/b]",
            markup=True,
            font_size=sp(24),
            color=(0.13, 0.59, 0.95, 1),
            size_hint_y=None,
            height=dp(34),
            halign="center",
        )
        app_name.bind(size=app_name.setter("text_size"))

        tagline = Label(
            text="Medicine Reminder",
            font_size=sp(14),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(22),
            halign="center",
        )
        tagline.bind(size=tagline.setter("text_size"))

        version = Label(
            text="Version 1.0.0",
            font_size=sp(13),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(20),
            halign="center",
        )
        version.bind(size=version.setter("text_size"))

        desc = Label(
            text="A modern medicine reminder app to help you\nstay on track with your medications.\nBuilt with Python & Kivy.",
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(60),
            halign="center",
            valign="top",
        )
        desc.bind(size=desc.setter("text_size"))

        copyright_lbl = Label(
            text="© 2026 MediCare",
            font_size=sp(11),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(20),
            halign="center",
        )
        copyright_lbl.bind(size=copyright_lbl.setter("text_size"))

        card.add_widget(app_name)
        card.add_widget(tagline)
        card.add_widget(version)
        card.add_widget(desc)
        card.add_widget(copyright_lbl)

        return card

    def _confirm_clear_history(self):
        """Confirm before clearing history."""
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        msg = Label(
            text="This will delete all medicine history records.\nThis action cannot be undone.",
            font_size=sp(14),
            color=(0.13, 0.13, 0.13, 1),
            halign="center",
            valign="center",
            size_hint_y=0.5,
        )
        msg.bind(size=msg.setter("text_size"))

        popup = Popup(
            title="Clear History?",
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

        clear_btn = Button(
            text="Clear All",
            font_size=sp(14),
            background_normal="",
            background_color=(0.96, 0.26, 0.21, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )

        def do_clear(x):
            from database import get_connection
            conn = get_connection()
            conn.execute("DELETE FROM history")
            conn.commit()
            conn.close()
            popup.dismiss()

        clear_btn.bind(on_release=do_clear)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(clear_btn)

        content.add_widget(msg)
        content.add_widget(btn_row)
        popup.open()

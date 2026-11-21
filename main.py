"""
MediCare – Medicine Reminder Application
Main entry point.
"""

import os
import sys

# Ensure the app directory is on sys.path so local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config

# Mobile-friendly configuration (must be set before any other Kivy import)
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")
Config.set("graphics", "resizable", "0")
Config.set("kivy", "window_icon", "")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window

import database
from reminder import ReminderManager
from screens.home_screen import HomeScreen
from screens.add_medicine_screen import AddMedicineScreen
from screens.medicines_screen import MedicinesScreen
from screens.history_screen import HistoryScreen
from screens.settings_screen import SettingsScreen


class NavBar(BoxLayout):
    """Bottom navigation bar with 4 tabs."""

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(58)
        self.padding = [0, 0]
        self.spacing = 0

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda *a: setattr(self._bg, "pos", self.pos),
            size=lambda *a: setattr(self._bg, "size", self.size),
        )

        # Thin top border
        with self.canvas.before:
            Color(0.88, 0.88, 0.88, 1)
            self._border = Rectangle(
                pos=self.pos, size=(self.width, dp(1))
            )
        self.bind(
            pos=lambda *a: setattr(self._border, "pos", self.pos),
            width=lambda *a: setattr(self._border, "size", (self.width, dp(1))),
        )

        self.tabs = {}
        tab_data = [
            ("home", "🏠\nHome"),
            ("medicines", "💊\nMedicines"),
            ("history", "📋\nHistory"),
            ("settings", "⚙️\nSettings"),
        ]

        for screen_name, label in tab_data:
            btn = Button(
                text=label,
                font_size=sp(11),
                halign="center",
                valign="center",
                background_normal="",
                background_color=(1, 1, 1, 0),
                color=(0.6, 0.6, 0.6, 1),
                markup=False,
            )
            btn.bind(size=btn.setter("text_size"))
            btn.bind(
                on_release=lambda x, sn=screen_name: self._switch(sn)
            )
            self.tabs[screen_name] = btn
            self.add_widget(btn)

        # Highlight initial tab
        self._highlight("home")

    def _switch(self, screen_name):
        """Switch to the given screen and highlight the tab."""
        if self.sm.current != screen_name:
            # Determine transition direction
            order = ["home", "medicines", "history", "settings"]
            current_idx = order.index(self.sm.current) if self.sm.current in order else 0
            target_idx = order.index(screen_name) if screen_name in order else 0
            self.sm.transition.direction = "left" if target_idx > current_idx else "right"
            self.sm.current = screen_name
        self._highlight(screen_name)

    def _highlight(self, active):
        """Highlight the active tab."""
        for name, btn in self.tabs.items():
            if name == active:
                btn.color = (0.13, 0.59, 0.95, 1)
                btn.bold = True
            else:
                btn.color = (0.6, 0.6, 0.6, 1)
                btn.bold = False

    def update_active(self, screen_name):
        """Update the highlight when screen changes externally."""
        if screen_name in self.tabs:
            self._highlight(screen_name)


class MediCareApp(App):
    """Main MediCare Application."""

    title = "MediCare"

    def build(self):
        # Set window background
        Window.clearcolor = (0.96, 0.97, 0.98, 1)

        # Initialize database
        database.init_db()

        # Build screen manager
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(AddMedicineScreen(name="add_medicine"))
        self.sm.add_widget(MedicinesScreen(name="medicines"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(SettingsScreen(name="settings"))

        # Main layout: screens + navbar
        root = BoxLayout(orientation="vertical")

        # Navigation bar
        self.navbar = NavBar(self.sm)

        # Listen for screen changes to update navbar
        self.sm.bind(current=self._on_screen_change)

        root.add_widget(self.sm)
        root.add_widget(self.navbar)

        # Start reminder system
        self.reminder_manager = ReminderManager(app=self)
        self.reminder_manager.start()

        return root

    def _on_screen_change(self, instance, value):
        """Update navbar when screen changes."""
        self.navbar.update_active(value)

    def on_pause(self):
        """Allow the app to pause on Android."""
        return True

    def on_resume(self):
        """Refresh data when app resumes."""
        try:
            screen = self.sm.get_screen(self.sm.current)
            if hasattr(screen, "refresh_data"):
                screen.refresh_data()
            elif hasattr(screen, "refresh_list"):
                screen.refresh_list()
            elif hasattr(screen, "refresh_history"):
                screen.refresh_history()
        except Exception:
            pass

    def on_stop(self):
        """Clean up when app stops."""
        if hasattr(self, "reminder_manager"):
            self.reminder_manager.stop()


if __name__ == "__main__":
    MediCareApp().run()

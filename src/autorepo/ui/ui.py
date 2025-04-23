import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.title("Automatic Repo Updater")
        self.geometry("800x600")
        self.configure_theme()

        self.update_button = ttk.Button(
            self, text="Update Repositories", command=self.update_repositories
        )
        self.update_button.pack(pady=20)

        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack()

        self.theme_button = ttk.Button(
            self, text="Toggle Theme", command=self.toggle_theme
        )
        self.theme_button.pack(pady=10)

    def configure_theme(self):
        """Configure the theme based on settings"""
        if self.settings.theme == "dark":
            self.style = ttk.Style(self)
            self.style.theme_use('clam')
            self.style.configure(
                ".",
                background="#222222",
                foreground="white"
            )
            self.style.configure(
                "TButton",
                background="#333333",
                foreground="white"
            )
        else:
            self.style = ttk.Style(self)
            self.style.theme_use('clam')
            self.style.configure(
                ".",
                background="white",
                foreground="black"
            )
            self.style.configure(
                "TButton",
                background="#dddddd",
                foreground="black"
            )

    def toggle_theme(self):
        """Toggle the theme and update the UI"""
        if self.settings.theme == "dark":
            self.settings.theme = "light"
        else:
            self.settings.theme = "dark"
        self.settings.save_settings()
        self.configure_theme()

    def update_repositories(self):
        """Update the repositories and display the status"""
        self.status_label.config(text="Updating...")
        # Add logic to update repositories here
        self.status_label.config(text="Update complete")

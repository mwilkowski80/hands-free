# handsfree/gui.py
import tkinter as tk
import logging
import platform

logger = logging.getLogger(__name__)

IS_LINUX = (platform.system().lower() == "linux")

if IS_LINUX:
    import gi
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3, Gtk, GLib
    except ValueError:
        logger.warning("LibAppIndicator (AppIndicator3) not available.")
        AppIndicator3 = None
        Gtk = None
        GLib = None

class HandsfreeTrayIndicator:
    def __init__(self, idle_icon_path, recording_icon_path, quit_callback=None):
        self.idle_icon_path = idle_icon_path
        self.recording_icon_path = recording_icon_path
        self._current_icon = None
        self.quit_callback = quit_callback

        self.indicator = AppIndicator3.Indicator.new(
            "handsfree-indicator",
            self.idle_icon_path,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()

        item_quit = Gtk.MenuItem(label="Quit Handsfree")
        item_quit.connect("activate", self._on_quit_clicked)
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def _on_quit_clicked(self, source):
        logger.info("Tray menu: quit clicked.")
        if self.quit_callback:
            self.quit_callback()
        else:
            import sys
            sys.exit(0)

    def set_icon_idle(self):
        if self._current_icon != "idle":
            self.indicator.set_icon_full(self.idle_icon_path, "idle")
            self._current_icon = "idle"

    def set_icon_recording(self):
        if self._current_icon != "recording":
            self.indicator.set_icon_full(self.recording_icon_path, "recording")
            self._current_icon = "recording"

class HandsfreeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Handsfree")
        self.root.geometry("200x100")
        self.status_label = tk.Label(self.root, text="Status: IDLE", font=("Arial", 14))
        self.status_label.pack(pady=20)

        self.on_close_callback = None
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

        self.tray = None
        if IS_LINUX and AppIndicator3 is not None:
            idle_icon_path = "handsfree/icons/idle.png"
            recording_icon_path = "handsfree/icons/recording.png"
            self.tray = HandsfreeTrayIndicator(
                idle_icon_path,
                recording_icon_path,
                quit_callback=self._handle_close
            )

    def set_status(self, status_text):
        self.status_label.config(text=f"Status: {status_text}")
        if self.tray:
            if status_text.upper() == "IDLE":
                self.tray.set_icon_idle()
            else:
                self.tray.set_icon_recording()

    def set_on_close_callback(self, callback):
        self.on_close_callback = callback

    def _handle_close(self, *args):
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.root.destroy()

    def run(self):
        if IS_LINUX and AppIndicator3 is not None and GLib is not None:
            from threading import Thread
            def run_glib():
                GLib.MainLoop().run()
            Thread(target=run_glib, daemon=True).start()

        self.root.mainloop()

    def close(self):
        self.root.destroy()

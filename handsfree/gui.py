# handsfree/gui.py

import tkinter as tk
import logging
import platform
import os

logger = logging.getLogger(__name__)

IS_LINUX = (platform.system().lower() == "linux")

if IS_LINUX:
    import gi
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3, Gtk, GLib
    except ValueError:
        logger.warning("LibAppIndicator (AppIndicator3) not available - tray icon won't work.")
        AppIndicator3 = None
        Gtk = None
        GLib = None


class HandsfreeTrayIndicator:
    """
    Tray icon manager on Linux using AppIndicator3.
    Supports three states: IDLE, RECORDING, PROCESSING.
    """

    def __init__(
        self,
        idle_icon_path,
        recording_icon_path,
        processing_icon_path,
        quit_callback=None
    ):
        """
        :param idle_icon_path: path to idle PNG icon
        :param recording_icon_path: path to recording PNG icon
        :param processing_icon_path: path to processing PNG icon
        :param quit_callback: function to call when "Quit Handsfree" is selected
        """
        self.idle_icon_path = idle_icon_path
        self.recording_icon_path = recording_icon_path
        self.processing_icon_path = processing_icon_path
        self._current_icon = None
        self.quit_callback = quit_callback

        # Create the AppIndicator
        if AppIndicator3 is None:
            logger.warning("AppIndicator3 not available. Tray icon will not appear.")
            return

        logger.debug("Creating AppIndicator with idle icon at: %s", self.idle_icon_path)
        self.indicator = AppIndicator3.Indicator.new(
            "handsfree-indicator",
            self.idle_icon_path,  # initial icon
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Create the tray menu
        self.menu = Gtk.Menu()

        # "Quit" menu item
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
        """
        Switch to the idle icon if not already active.
        """
        if AppIndicator3 is None:
            return  # No AppIndicator support
        if self._current_icon != "idle":
            logger.debug("Setting tray icon to IDLE: %s", self.idle_icon_path)
            self.indicator.set_icon_full(self.idle_icon_path, "idle")
            self._current_icon = "idle"

    def set_icon_recording(self):
        """
        Switch to the recording icon if not already active.
        """
        if AppIndicator3 is None:
            return
        if self._current_icon != "recording":
            logger.debug("Setting tray icon to RECORDING: %s", self.recording_icon_path)
            self.indicator.set_icon_full(self.recording_icon_path, "recording")
            self._current_icon = "recording"

    def set_icon_processing(self):
        """
        Switch to the processing icon if not already active.
        """
        if AppIndicator3 is None:
            return
        if self._current_icon != "processing":
            logger.debug("Setting tray icon to PROCESSING: %s", self.processing_icon_path)
            self.indicator.set_icon_full(self.processing_icon_path, "processing")
            self._current_icon = "processing"


class HandsfreeGUI:
    """
    Main GUI for Handsfree:
    - A Tkinter window that shows the status (IDLE/RECORDING/PROCESSING).
    - An optional tray icon on Linux with AppIndicator3.
    """

    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Handsfree")
        self.root.geometry("200x100")

        # A label to display status
        self.status_label = tk.Label(self.root, text="Status: IDLE", font=("Arial", 14))
        self.status_label.pack(pady=20)

        # Callback for closing the app
        self.on_close_callback = None
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

        # Only create the tray if on Linux + AppIndicator3 is available
        self.tray = None
        if IS_LINUX and AppIndicator3 is not None:
            # You can use absolute paths if relative ones cause issues
            idle_icon_path = os.path.abspath("handsfree/icons/idle-symbolic.svg")
            recording_icon_path = os.path.abspath("handsfree/icons/recording-symbolic.svg")
            processing_icon_path = os.path.abspath("handsfree/icons/processing-symbolic.svg")

            # Debug logs to see if files exist
            logger.debug("Paths for tray icons:\n  idle=%s\n  recording=%s\n  processing=%s",
                         idle_icon_path,
                         recording_icon_path,
                         processing_icon_path)

            self.tray = HandsfreeTrayIndicator(
                idle_icon_path,
                recording_icon_path,
                processing_icon_path,
                quit_callback=self._handle_close
            )

    def set_status(self, status_text):
        """
        Update the label and, if on Linux, switch the tray icon.
        Supported status_text values: "IDLE", "RECORDING", "PROCESSING" (case-insensitive).
        """
        self.status_label.config(text=f"Status: {status_text}")
        logger.debug("GUI status changed to: %s", status_text)

        # If there's a tray, switch icons
        if self.tray:
            status_upper = status_text.upper()
            if status_upper == "IDLE":
                self.tray.set_icon_idle()
            elif status_upper == "RECORDING":
                self.tray.set_icon_recording()
            elif status_upper == "PROCESSING":
                self.tray.set_icon_processing()
            else:
                # Fallback if unknown status
                self.tray.set_icon_idle()

    def set_on_close_callback(self, callback):
        """
        Allows the main script to define what should happen when the user closes the window or
        clicks Quit in the tray.
        """
        self.on_close_callback = callback

    def _handle_close(self, *args):
        if self.on_close_callback:
            self.on_close_callback()
        else:
            # Fallback: just destroy the Tk window
            self.root.destroy()

    def run(self):
        """
        Start the Tk event loop.
        Also start the GLib main loop on a background thread if we're on Linux with an AppIndicator,
        so the tray menu remains responsive.
        """
        if IS_LINUX and AppIndicator3 is not None and GLib is not None:
            from threading import Thread

            def run_glib():
                GLib.MainLoop().run()

            Thread(target=run_glib, daemon=True).start()

        self.root.mainloop()

    def close(self):
        """
        Allows the main script to programmatically close the GUI.
        """
        self.root.destroy()

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
        logger.warning("LibAppIndicator (AppIndicator3) not available - tray icon won't work." )
        AppIndicator3 = None
        Gtk = None
        GLib = None

class HandsfreeTrayIndicator:
    """
    Obsługuje ikonę w trayu na Linuksie z użyciem AppIndicator3.
    """
    def __init__(self, idle_icon_path, recording_icon_path):
        self.idle_icon_path = idle_icon_path
        self.recording_icon_path = recording_icon_path
        self._current_icon = None

        # Utwórz wskaźnik (indicator) AppIndicator
        self.indicator = AppIndicator3.Indicator.new(
            "handsfree-indicator",
            self.idle_icon_path,  # startowo idle
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        # Ustaw status, żeby ikona była aktywna
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Stwórz minimalne menu, aby dało się np. zakończyć aplikację
        self.menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label="Quit Handsfree")
        item_quit.connect("activate", self._on_quit_clicked)
        self.menu.append(item_quit)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def _on_quit_clicked(self, source):
        """
        Możesz tutaj np. wywołać callback do zamknięcia głównego okna,
        albo zrobić cokolwiek innego.
        """
        logger.info("Tray menu: quit clicked")
        # Najprostsze rozwiązanie - zabij proces
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
    """
    Proste okno w Tkinter z etykietą statusu.
    Jeśli jesteśmy na Linuksie i mamy AppIndicator3, tworzymy też ikonę w trayu.
    """
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
            # Utwórz tray icon
            idle_icon_path = "handsfree/icons/idle.png"
            recording_icon_path = "handsfree/icons/recording.png"
            self.tray = HandsfreeTrayIndicator(idle_icon_path, recording_icon_path)

    def set_status(self, status_text):
        """
        Ustawia tekst wyświetlany w oknie
        i ewentualnie aktualizuje ikonę w trayu.
        """
        self.status_label.config(text=f"Status: {status_text}")

        if self.tray:
            if status_text.upper() == "IDLE":
                self.tray.set_icon_idle()
            else:
                # "RECORDING", "PROCESSING", etc.
                self.tray.set_icon_recording()

    def set_on_close_callback(self, callback):
        self.on_close_callback = callback

    def _handle_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.root.destroy()

    def run(self):
        # Na Linuksie, aby AppIndicator działał, musimy w pętli tkinter wykonać integrację z GLib
        if IS_LINUX and AppIndicator3 is not None and GLib is not None:
            # Uruchamiamy wątek GLib, żeby ikona reagowała na menu
            # i była "na żywo" aktualizowana
            from threading import Thread
            def run_glib():
                GLib.MainLoop().run()

            Thread(target=run_glib, daemon=True).start()

        self.root.mainloop()

    def close(self):
        self.root.destroy()

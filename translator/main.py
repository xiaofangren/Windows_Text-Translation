import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PyQt6.QtCore import QTimer, Qt
from config import APP_NAME, APP_VERSION, DEFAULT_APP_ID
from settings import SettingsManager
from translator import TranslatorManager
from hotkey_listener import SelectionMonitor
from popup_window import PopupWindow
from system_tray import SystemTray
from settings_dialog import SettingsDialog


class MainWindow:
    def __init__(self):
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(APP_NAME)
            self.app.setApplicationVersion(APP_VERSION)
            self.app.setQuitOnLastWindowClosed(False)

            self.settings_manager = SettingsManager()
            self.translator_manager = TranslatorManager()
            self.popup_window = PopupWindow()

            self.is_translating = False

            self.setup_tray()
            self.setup_monitor()
            self.setup_translator()
        except Exception:
            traceback.print_exc()
            raise

    def setup_tray(self):
        self.tray = SystemTray()
        self.tray.show()

        self.tray.show_settings_action.triggered.connect(self.show_settings)
        self.tray.quit_action.triggered.connect(self.quit_app)
        self.tray.activated.connect(self.on_tray_activated)

    def setup_monitor(self):
        self.selection_monitor = SelectionMonitor(self.on_hotkey_triggered)
        self.selection_monitor.start()

    def setup_translator(self):
        app_id = self.settings_manager.get_app_id()
        secret_key = self.settings_manager.get_secret_key()
        self.translator_manager.set_baidu_credentials(app_id, secret_key)

        engine = self.settings_manager.get_translate_engine()
        self.translator_manager.set_current_engine(engine)

    def on_hotkey_triggered(self, selected_text):
        if self.is_translating:
            return
        self.is_translating = True

        self.popup_window.hide()

        QTimer.singleShot(50, lambda: self.do_translate(selected_text))

    def do_translate(self, selected_text):
        try:
            clean_text = selected_text.strip()

            if not clean_text:
                self.is_translating = False
                self.selection_monitor.notify_translation_done()
                return

            result = self.translator_manager.translate(clean_text)

            if result and not result.startswith("[错误]"):
                self.popup_window.show_translation(
                    clean_text[:200],
                    result,
                )
            elif not result:
                self.tray.showMessage(
                    "Translation", "No translation result returned."
                )
            else:
                self.tray.showMessage(
                    "Translation Error", result
                )
        except Exception:
            error_msg = traceback.format_exc()
            self.tray.showMessage("Error", f"Translation failed: {error_msg[:200]}")
        finally:
            self.is_translating = False
            self.selection_monitor.notify_translation_done()

    def show_settings(self):
        dialog = SettingsDialog(self.settings_manager)
        if dialog.exec():
            app_id = self.settings_manager.get_app_id()
            secret_key = self.settings_manager.get_secret_key()
            self.translator_manager.set_baidu_credentials(app_id, secret_key)

            engine = self.settings_manager.get_translate_engine()
            self.translator_manager.set_current_engine(engine)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()

    def quit_app(self):
        self.selection_monitor.stop()
        self.app.quit()

    def run(self):
        if self.settings_manager.get_app_id() == DEFAULT_APP_ID:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Welcome to QuickTranslator")
            msg.setText("First time setup: please configure Baidu Translate API")
            msg.setInformativeText(
                "Right-click the system tray icon and select 'Settings' to enter your App ID and Secret Key.\n\n"
                "Visit https://fanyi-api.baidu.com/ to get a free API key."
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

            self.show_settings()

        return self.app.exec()


if __name__ == "__main__":
    try:
        window = MainWindow()
        sys.exit(window.run())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

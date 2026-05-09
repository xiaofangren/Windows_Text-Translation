import sys
from PyQt6.QtWidgets import QApplication


IS_WINDOWS = sys.platform == "win32"


class ClipboardManager:
    def __init__(self):
        self.clipboard = QApplication.clipboard()

    def get_text(self):
        try:
            mime_data = self.clipboard.mimeData()
            if mime_data and mime_data.hasText():
                return mime_data.text()
        except Exception:
            pass
        return ""

    def set_text(self, text):
        try:
            self.clipboard.setText(text)
        except Exception:
            pass

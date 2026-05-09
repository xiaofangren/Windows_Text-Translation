from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QFont
from config import APP_NAME, APP_VERSION


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = self.create_default_icon()
        super().__init__(icon, parent)

        self.menu = QMenu()

        self.show_settings_action = QAction("Settings", self)
        self.menu.addAction(self.show_settings_action)

        self.menu.addSeparator()

        self.quit_action = QAction("Quit", self)
        self.menu.addAction(self.quit_action)

        self.setContextMenu(self.menu)

        self.setToolTip(f"{APP_NAME} v{APP_VERSION}")

    def create_default_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#4CAF50"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 36)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), 0x04, "T")
        painter.end()
        return QIcon(pixmap)

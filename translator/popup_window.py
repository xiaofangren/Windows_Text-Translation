from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QCursor
from config import (
    WINDOW_MAX_WIDTH,
    WINDOW_MAX_HEIGHT,
    WINDOW_PADDING,
    WINDOW_OFFSET_X,
    WINDOW_OFFSET_Y,
)


class PopupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(WINDOW_PADDING, WINDOW_PADDING, WINDOW_PADDING, WINDOW_PADDING)

        self.original_label = QLabel()
        self.original_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                font-size: 12px;
                padding: 5px;
                background-color: rgba(240, 240, 240, 220);
                border-radius: 4px;
            }
            """
        )
        self.original_label.setWordWrap(True)
        self.original_label.setMaximumWidth(WINDOW_MAX_WIDTH - WINDOW_PADDING * 2)
        main_layout.addWidget(self.original_label)

        self.translated_label = QLabel()
        self.translated_label.setStyleSheet(
            """
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: rgba(255, 255, 255, 240);
                border-radius: 4px;
            }
            """
        )
        self.translated_label.setWordWrap(True)
        self.translated_label.setMaximumWidth(WINDOW_MAX_WIDTH - WINDOW_PADDING * 2)
        self.translated_label.setMaximumHeight(WINDOW_MAX_HEIGHT - WINDOW_PADDING * 4 - 40)
        main_layout.addWidget(self.translated_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedSize(50, 25)
        self.copy_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            """
        )
        self.copy_btn.clicked.connect(self.copy_translation)
        button_layout.addWidget(self.copy_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedSize(50, 25)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41709;
            }
            """
        )
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)

        main_layout.addLayout(button_layout)

        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(245, 245, 245, 240);
                border-radius: 6px;
            }
            """
        )

        self.setLayout(main_layout)
        self.adjustSize()

    def show_translation(self, original_text, translated_text, position=None):
        self.original_label.setText(original_text)
        self.translated_label.setText(translated_text)

        self.adjustSize()

        if position is None:
            cursor_pos = QCursor.pos()
        else:
            cursor_pos = position

        x = cursor_pos.x() + WINDOW_OFFSET_X
        y = cursor_pos.y() + WINDOW_OFFSET_Y

        screen_at_cursor = QApplication.screenAt(cursor_pos)
        if screen_at_cursor:
            screen = screen_at_cursor.availableGeometry()
        else:
            screen = QApplication.primaryScreen().availableGeometry()
        if x + self.width() > screen.right():
            x = cursor_pos.x() - self.width() - WINDOW_OFFSET_X
        if y + self.height() > screen.bottom():
            y = cursor_pos.y() - self.height() - WINDOW_OFFSET_Y

        x = max(screen.left(), x)
        y = max(screen.top(), y)

        self.move(x, y)
        self.show()
        self.auto_hide_timer.start(15000)

    def copy_translation(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.translated_label.text())
        self.copy_btn.setText("Copied")
        self.copy_btn.repaint()
        self.auto_hide_timer.start(15000)
        QTimer.singleShot(1000, lambda: self.copy_btn.setText("Copy"))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.auto_hide_timer.start(15000)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.auto_hide_timer.start(15000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        super().keyPressEvent(event)

    def hideEvent(self, event):
        self.auto_hide_timer.stop()
        super().hideEvent(event)

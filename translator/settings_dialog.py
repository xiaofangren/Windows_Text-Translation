from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from config import (
    DEFAULT_APP_ID,
    DEFAULT_SECRET_KEY,
    DEFAULT_TRANSLATE_ENGINE,
    SUPPORTED_ENGINES,
    APP_NAME,
)


class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        usage_group = QGroupBox("How to use")
        usage_layout = QVBoxLayout()
        usage_label = QLabel(
            "Select text with your mouse in any application.\n"
            "A green '译' button will appear near the cursor.\n"
            "Click it to translate."
        )
        usage_label.setWordWrap(True)
        usage_label.setStyleSheet("color: #666; font-size: 12px;")
        usage_layout.addWidget(usage_label)
        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)

        api_group = QGroupBox("Baidu Translate API")
        api_layout = QVBoxLayout()

        app_id_layout = QHBoxLayout()
        app_id_label = QLabel("App ID:")
        app_id_label.setFixedWidth(80)
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("Enter Baidu Translate App ID")
        app_id_layout.addWidget(app_id_label)
        app_id_layout.addWidget(self.app_id_input)
        api_layout.addLayout(app_id_layout)

        secret_key_layout = QHBoxLayout()
        secret_key_label = QLabel("Secret Key:")
        secret_key_label.setFixedWidth(80)
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter Baidu Translate Secret Key")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        secret_key_layout.addWidget(secret_key_label)
        secret_key_layout.addWidget(self.secret_key_input)
        api_layout.addLayout(secret_key_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        engine_group = QGroupBox("Translation Engine")
        engine_layout = QHBoxLayout()

        engine_label = QLabel("Engine:")
        engine_label.setFixedWidth(80)
        self.engine_combo = QComboBox()
        for engine in SUPPORTED_ENGINES:
            self.engine_combo.addItem(engine)
        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self.engine_combo)
        engine_group.setLayout(engine_layout)
        layout.addWidget(engine_group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setFixedWidth(80)
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(80)
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            """
        )
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        app_id = self.settings_manager.get_app_id()
        if app_id != DEFAULT_APP_ID:
            self.app_id_input.setText(app_id)

        secret_key = self.settings_manager.get_secret_key()
        if secret_key != DEFAULT_SECRET_KEY:
            self.secret_key_input.setText(secret_key)

        engine = self.settings_manager.get_translate_engine()
        for i in range(self.engine_combo.count()):
            if self.engine_combo.itemText(i) == engine:
                self.engine_combo.setCurrentIndex(i)
                break

    def save_settings(self):
        app_id = self.app_id_input.text().strip()
        secret_key = self.secret_key_input.text().strip()

        if not app_id or not secret_key:
            QMessageBox.warning(
                self, "Warning", "Please fill in App ID and Secret Key"
            )
            return

        self.settings_manager.set_app_id(app_id)
        self.settings_manager.set_secret_key(secret_key)

        engine = self.engine_combo.currentText()
        self.settings_manager.set_translate_engine(engine)

        self.settings_manager.sync()

        QMessageBox.information(self, "Info", "Settings saved")
        self.accept()

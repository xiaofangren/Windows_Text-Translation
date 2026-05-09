from PyQt6.QtCore import QSettings
from config import (
    APP_NAME,
    DEFAULT_APP_ID,
    DEFAULT_SECRET_KEY,
    DEFAULT_TRANSLATE_ENGINE,
    ORG_NAME,
)


class SettingsManager:
    def __init__(self):
        self.settings = QSettings(ORG_NAME, APP_NAME)

    def get_app_id(self):
        return self.settings.value("baidu_app_id", DEFAULT_APP_ID)

    def set_app_id(self, app_id):
        self.settings.setValue("baidu_app_id", app_id)

    def get_secret_key(self):
        return self.settings.value("baidu_secret_key", DEFAULT_SECRET_KEY)

    def set_secret_key(self, secret_key):
        self.settings.setValue("baidu_secret_key", secret_key)

    def get_translate_engine(self):
        return self.settings.value("translate_engine", DEFAULT_TRANSLATE_ENGINE)

    def set_translate_engine(self, engine):
        self.settings.setValue("translate_engine", engine)

    def sync(self):
        self.settings.sync()

import hashlib
import random
import requests
from config import BAIDU_TRANSLATE_API_URL, LANG_AUTO, LANG_ZH, REQUEST_TIMEOUT, MAX_TEXT_LENGTH


class BaiduTranslator:
    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key

    def translate(self, text, from_lang=LANG_AUTO, to_lang=LANG_ZH):
        if not text or not text.strip():
            return ""

        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]

        salt = str(random.randint(32768, 65536))
        sign_str = self.app_id + text + salt + self.secret_key
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

        params = {
            "q": text,
            "from": from_lang,
            "to": to_lang,
            "appid": self.app_id,
            "salt": salt,
            "sign": sign,
        }

        try:
            response = requests.post(
                BAIDU_TRANSLATE_API_URL, data=params, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()

            if "error_code" in result:
                return f"[错误] {result.get('error_msg', '未知错误')}"

            trans_result = result.get("trans_result", [])
            if trans_result:
                return "\n".join([item["dst"] for item in trans_result])
            return ""
        except requests.exceptions.Timeout:
            return "[错误] 请求超时"
        except requests.exceptions.RequestException as e:
            return f"[错误] 网络异常: {str(e)}"
        except Exception as e:
            return f"[错误] {str(e)}"


class TranslatorManager:
    def __init__(self):
        self.translators = {}
        self.current_engine = None

    def set_baidu_credentials(self, app_id, secret_key):
        self.translators["baidu"] = BaiduTranslator(app_id, secret_key)

    def set_current_engine(self, engine):
        if engine in self.translators:
            self.current_engine = engine

    def translate(self, text, from_lang=LANG_AUTO, to_lang=LANG_ZH):
        if not self.current_engine or self.current_engine not in self.translators:
            return "[错误] 未配置翻译引擎"

        translator = self.translators[self.current_engine]
        return translator.translate(text, from_lang, to_lang)

import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

user32 = ctypes.windll.user32
user32.OpenClipboard(None)
CF_TEXT = 1
handle = user32.GetClipboardData(CF_TEXT)
if handle:
    kernel32 = ctypes.windll.kernel32
    text_ptr = kernel32.GlobalLock(handle)
    if text_ptr:
        text = ctypes.c_char_p(text_ptr).value
        kernel32.GlobalUnlock(handle)
    user32.CloseClipboard()
    print(f"Win32 clipboard: {repr(text[:100] if text else 'empty')}")
else:
    user32.CloseClipboard()
    print("Win32 clipboard: empty")
    
qt_text = app.clipboard().text()
print(f"Qt clipboard: {repr(qt_text[:100] if qt_text else 'empty')}")

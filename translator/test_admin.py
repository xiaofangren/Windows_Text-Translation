import sys
import time
import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QApplication


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long), ("dy", ctypes.c_long),
        ("mouseData", ctypes.wintypes.DWORD), ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD), ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD), ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD), ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.wintypes.DWORD), ("union", INPUT_UNION),
    ]


app = QApplication(sys.argv)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11

hwnd = user32.GetForegroundWindow()
sb = ctypes.create_unicode_buffer(256)
user32.GetWindowTextW(hwnd, sb, 256)
print(f"当前窗口: {sb.value}")
print(f"当前用户: Admin={ctypes.windll.shell32.IsUserAnAdmin()}")
print(f"sizeof(INPUT) = {ctypes.sizeof(INPUT)}")
print()
print("请在 5 秒内切换到浏览器并选中一些文字...")
time.sleep(5)

hwnd2 = user32.GetForegroundWindow()
sb2 = ctypes.create_unicode_buffer(256)
user32.GetWindowTextW(hwnd2, sb2, 256)
print(f"目标窗口: {sb2.value}")

inputs = (INPUT * 4)()
inputs[0].type = INPUT_KEYBOARD
inputs[0].union.ki = KEYBDINPUT(VK_CONTROL, 0, 0, 0, 0)
inputs[1].type = INPUT_KEYBOARD
inputs[1].union.ki = KEYBDINPUT(ord("C"), 0, 0, 0, 0)
inputs[2].type = INPUT_KEYBOARD
inputs[2].union.ki = KEYBDINPUT(ord("C"), 0, KEYEVENTF_KEYUP, 0, 0)
inputs[3].type = INPUT_KEYBOARD
inputs[3].union.ki = KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, 0)

result = user32.SendInput(4, inputs, ctypes.sizeof(INPUT))
print(f"SendInput result: {result}")

if result == 0:
    err = kernel32.GetLastError()
    print(f"GetLastError: {err} (5=拒绝访问, 87=参数错误)")

time.sleep(0.3)
text = app.clipboard().text()
if text and text.strip():
    print(f"成功! 剪贴板: {repr(text[:200])}")
else:
    print("失败: 剪贴板为空")

input("\n按回车退出...")

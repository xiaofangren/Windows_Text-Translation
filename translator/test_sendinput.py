import time
import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QApplication
import sys

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


print(f"sizeof(KEYBDINPUT) = {ctypes.sizeof(KEYBDINPUT)}")
print(f"sizeof(MOUSEINPUT) = {ctypes.sizeof(MOUSEINPUT)}")
print(f"sizeof(HARDWAREINPUT) = {ctypes.sizeof(HARDWAREINPUT)}")
print(f"sizeof(INPUT) = {ctypes.sizeof(INPUT)}")

app = QApplication(sys.argv)

print("\n请清空剪贴板（在 cmd 里运行: echo off | clip）")
print("然后在记事本或浏览器中选中一些文字")
input("准备好后按回车...")

print("请在 5 秒内切换到选好文字的窗口...")
time.sleep(5)
print("正在测试 SendInput 模拟 Ctrl+C...")

user32 = ctypes.windll.user32

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
print(f"SendInput result: {result} (should be 4)")

time.sleep(0.3)

qt_text = app.clipboard().text()
if qt_text and qt_text.strip():
    print(f"\n成功! 剪贴板内容: {repr(qt_text[:200])}")
else:
    print("\n剪贴板为空")

input("\n按回车退出...")

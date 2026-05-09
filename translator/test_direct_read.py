import sys
import ctypes
import ctypes.wintypes

WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
EM_GETSEL = 0x00B0


def test_direct_read():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    foreground = user32.GetForegroundWindow()
    if not foreground:
        print("FAIL: no foreground window")
        return

    print(f"Foreground window handle: {foreground:#x}")

    foreground_tid = user32.GetWindowThreadProcessId(foreground, None)
    current_tid = kernel32.GetCurrentThreadId()

    attached = False
    if foreground_tid != current_tid:
        user32.AttachThreadInput(current_tid, foreground_tid, True)
        attached = True

    focused = user32.GetFocus()

    if attached:
        user32.AttachThreadInput(current_tid, foreground_tid, False)

    if not focused:
        focused = foreground
        print(f"No focused control, using foreground window: {focused:#x}")
    else:
        print(f"Focused control handle: {focused:#x}")

    text_len = user32.SendMessageW(focused, WM_GETTEXTLENGTH, 0, 0)
    if not text_len or text_len > 20000:
        print(f"FAIL: WM_GETTEXTLENGTH returned {text_len}")
        return

    print(f"Text length: {text_len}")

    buf = ctypes.create_unicode_buffer(text_len + 1)
    user32.SendMessageW(focused, WM_GETTEXT, text_len + 1, buf)
    full_text = buf.value

    if not full_text:
        print("FAIL: WM_GETTEXT returned empty")
        return

    print(f"Full text: {repr(full_text[:200])}")

    sel = user32.SendMessageW(focused, EM_GETSEL, 0, 0)
    sel_start = sel & 0xFFFF
    sel_end = (sel >> 16) & 0xFFFF

    print(f"Selection: start={sel_start}, end={sel_end}")

    if sel_end > sel_start:
        selected = full_text[sel_start:sel_end]
        print(f"Selected text: {repr(selected[:200])}")
    else:
        print("No text selected (selection range is empty)")


if __name__ == "__main__":
    print("请在5秒内点击到文本输入框并选中一些文字...")
    import time
    time.sleep(5)
    print("正在读取...")
    print()
    test_direct_read()

    input("\n按回车退出...")

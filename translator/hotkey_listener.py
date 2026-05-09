import sys
import queue
import threading
import time
import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

IS_WINDOWS = sys.platform == "win32"

BUTTON_SIZE = 34
BUTTON_TIMEOUT_MS = 2000
POLL_INTERVAL_MS = 30
DRAG_THRESHOLD = 8

WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
EM_GETSEL = 0x00B0
VK_CONTROL = 0x11


HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_int,
    ctypes.c_ssize_t,
    ctypes.c_ssize_t,
)


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt_x", ctypes.c_long), ("pt_y", ctypes.c_long),
        ("mouseData", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


def get_mouse_pos(lParam):
    try:
        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        return info.pt_x, info.pt_y
    except Exception:
        return 0, 0


def get_focused_control():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return None, None
    foreground_tid = user32.GetWindowThreadProcessId(foreground, None)
    current_tid = kernel32.GetCurrentThreadId()
    focused = None
    if foreground_tid != current_tid:
        user32.AttachThreadInput(current_tid, foreground_tid, True)
        focused = user32.GetFocus()
        user32.AttachThreadInput(current_tid, foreground_tid, False)
    else:
        focused = user32.GetFocus()
    return foreground, (focused if focused else foreground)


def get_selected_text_direct():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    foreground = user32.GetForegroundWindow()
    if not foreground:
        return None
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
    text_len = user32.SendMessageW(focused, WM_GETTEXTLENGTH, 0, 0)
    if not text_len or text_len > 20000:
        return None
    buf = ctypes.create_unicode_buffer(text_len + 1)
    user32.SendMessageW(focused, WM_GETTEXT, text_len + 1, buf)
    full_text = buf.value
    if not full_text:
        return None
    sel = user32.SendMessageW(focused, EM_GETSEL, 0, 0)
    sel_start = sel & 0xFFFF
    sel_end = (sel >> 16) & 0xFFFF
    if sel_end > sel_start:
        return full_text[sel_start:sel_end]
    return None


def _uia_walk_tree(root, max_nodes=500):
    if not root:
        return
    to_visit = [root]
    visited = 0
    while to_visit and visited < max_nodes:
        control = to_visit.pop(0)
        visited += 1
        yield control
        try:
            to_visit.extend(control.GetChildren())
        except Exception:
            pass


def _uia_has_text_selection():
    try:
        import uiautomation as auto
    except ImportError:
        return True
    try:
        user32 = ctypes.windll.user32
    except Exception:
        return True
    try:
        fg = user32.GetForegroundWindow()
        if not fg:
            return False
        root = auto.ControlFromHandle(fg)
        if not root:
            return False
        for control in _uia_walk_tree(root):
            if _uia_check_text_selection(control):
                return True
        return False
    except Exception:
        return True


def _uia_check_text_selection(control):
    if not control:
        return False
    try:
        tp = control.GetTextPattern()
    except Exception:
        return False
    if not tp:
        return False
    try:
        ranges = tp.GetSelection()
    except Exception:
        return False
    if not ranges:
        return False
    for r in ranges:
        try:
            txt = r.GetText(-1)
            if txt and txt.strip():
                return True
        except Exception:
            continue
    return False


def _uia_get_selected_text():
    try:
        import uiautomation as auto
    except ImportError:
        return None
    try:
        user32 = ctypes.windll.user32
    except Exception:
        return None
    try:
        fg = user32.GetForegroundWindow()
        if not fg:
            return None
        root = auto.ControlFromHandle(fg)
        if not root:
            return None
        for control in _uia_walk_tree(root):
            text = _uia_read_selection(control)
            if text:
                return text
    except Exception:
        pass
    return None


def _uia_read_selection(control):
    if not control:
        return None
    try:
        tp = control.GetTextPattern()
    except Exception:
        return None
    if not tp:
        return None
    try:
        ranges = tp.GetSelection()
    except Exception:
        return None
    if not ranges:
        return None
    for r in ranges:
        try:
            txt = r.GetText(-1)
            if txt and txt.strip():
                return txt.strip()
        except Exception:
            continue
    return None


def get_valid_selection_text():
    text = get_selected_text_direct()
    if text and text.strip():
        clean = text.strip()
        if len(clean) >= 2:
            if len(clean) > 500:
                clean = clean[:500] + "\u2026"
            return clean
    uia_text = _uia_get_selected_text()
    if uia_text and len(uia_text) >= 2:
        if len(uia_text) > 500:
            uia_text = uia_text[:500] + "\u2026"
        return uia_text
    return None


def simulate_ctrl_c():
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(ord("C"), 0, 0, 0)
    user32.keybd_event(ord("C"), 0, 2, 0)
    user32.keybd_event(VK_CONTROL, 0, 2, 0)


class FloatingTranslateButton(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)

        self._btn = QPushButton("\u8bd1", self)
        self._btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self._btn.setStyleSheet(
            """
            QPushButton {
                background-color: #43A047;
                color: white;
                border-radius: 17px;
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #388E3C;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            """
        )
        self._btn.clicked.connect(self._on_click)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

        self._busy = False
        self._button_center = None
        self._source_hwnd = None

    def show_at(self, x, y, source_hwnd):
        self._source_hwnd = source_hwnd
        self.move(x + 8, y + 8)
        self._button_center = (x + 8 + BUTTON_SIZE // 2, y + 8 + BUTTON_SIZE // 2)
        self.showNormal()
        self.raise_()
        self.show()
        self._hide_timer.start(BUTTON_TIMEOUT_MS)

    def _on_click(self):
        if self._busy:
            return
        self._hide_timer.stop()
        self.hide()
        self._busy = True

        text = get_valid_selection_text()
        if text:
            self._busy = False
            self.clicked.emit(text)
            return

        QTimer.singleShot(30, self._activate_and_copy)

    def _activate_and_copy(self):
        user32 = ctypes.windll.user32

        target = self._source_hwnd
        if not target or not user32.IsWindow(target):
            target = user32.GetForegroundWindow()

        self._source_hwnd = target
        user32.SetForegroundWindow(target)
        QTimer.singleShot(60, self._do_copy)

    def _do_copy(self):
        simulate_ctrl_c()
        QTimer.singleShot(200, self._read_and_translate)

    def _read_and_translate(self):
        app = QApplication.instance()
        try:
            text = app.clipboard().text().strip()
        except Exception:
            text = ""
        self._busy = False
        if text and len(text) >= 2:
            if len(text) > 500:
                text = text[:500] + "\u2026"
            self.clicked.emit(text)

    def hideEvent(self, event):
        self._button_center = None
        super().hideEvent(event)


class SelectionMonitor:
    def __init__(self, callback):
        self._callback = callback
        self._running = False
        self._floating_btn = None
        self._event_queue = None
        self._poll_timer = None
        self._translating = False
        self._hook_thread = None
        self._hook_id = None
        self._last_hwnd = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._floating_btn = FloatingTranslateButton()
        self._floating_btn.clicked.connect(self._on_translate)
        self._event_queue = queue.Queue()
        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._poll_events)
        self._poll_timer.start(POLL_INTERVAL_MS)
        if IS_WINDOWS:
            self._start_mouse_hook()

    def _start_mouse_hook(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ]
        user32.SetWindowsHookExW.restype = ctypes.c_void_p
        user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t, ctypes.c_ssize_t]
        user32.CallNextHookEx.restype = ctypes.c_ssize_t
        event_queue = self._event_queue
        mouse_down_pos = [0, 0]

        def hook_proc(nCode, wParam, lParam):
            if nCode >= 0:
                x, y = get_mouse_pos(lParam)
                if wParam == WM_LBUTTONDOWN:
                    mouse_down_pos[0] = x
                    mouse_down_pos[1] = y
                elif wParam == WM_LBUTTONUP:
                    dx = x - mouse_down_pos[0]
                    dy = y - mouse_down_pos[1]
                    if dx * dx + dy * dy >= DRAG_THRESHOLD * DRAG_THRESHOLD:
                        event_queue.put((x, y))
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        callback_ptr = HOOKPROC(hook_proc)
        self._mouse_callback = callback_ptr

        def run_hook():
            try:
                hook_id = user32.SetWindowsHookExW(
                    WH_MOUSE_LL, callback_ptr, None, 0,
                )
                if not hook_id:
                    return
                self._hook_id = hook_id
                msg = ctypes.wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
            except Exception:
                pass

        self._hook_thread = threading.Thread(target=run_hook, daemon=True)
        self._hook_thread.start()

    def _poll_events(self):
        if self._translating:
            return
        if not self._floating_btn:
            return
        try:
            while True:
                x, y = self._event_queue.get_nowait()
                self._on_mouse_release(x, y)
        except queue.Empty:
            pass

    def _on_mouse_release(self, x, y):
        btn = self._floating_btn
        if btn._button_center:
            bx, by = btn._button_center
            if abs(x - bx) < BUTTON_SIZE and abs(y - by) < BUTTON_SIZE:
                btn._button_center = None
                return
        btn._button_center = None
        if btn._busy:
            return
        btn.hide()

        user32 = ctypes.windll.user32
        current_hwnd = user32.GetForegroundWindow()

        text = get_selected_text_direct()
        if text is None:
            if not _uia_has_text_selection():
                return
            btn.show_at(x, y, current_hwnd)
            return

        if text and text.strip():
            btn.show_at(x, y, current_hwnd)

    def _on_translate(self, text):
        if not text:
            return
        self._translating = True
        self._callback(text)

    def notify_translation_done(self):
        self._translating = False

    def stop(self):
        self._running = False
        if self._poll_timer:
            self._poll_timer.stop()
            self._poll_timer = None
        if self._hook_id:
            try:
                user32 = ctypes.windll.user32
                user32.PostThreadMessageW(
                    self._hook_thread.ident if self._hook_thread else 0,
                    0x0012, 0, 0,
                )
            except Exception:
                pass
            self._hook_id = None
            self._hook_thread = None
        if self._floating_btn:
            self._floating_btn.hide()
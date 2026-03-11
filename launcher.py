"""
launcher.py — «На авось», однофайловый exe.

Сборка:
    pyinstaller build_windows.spec
"""

import sys
import ctypes
import threading
import socket
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import webview
from bridge import Bridge


def base_path() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def find_free_port() -> int:
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def make_handler(html: bytes):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *args):
            pass  # подавляем вывод в консоль

    return Handler


def start_server(html: bytes, port: int):
    server = HTTPServer(('127.0.0.1', port), make_handler(html))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def set_icons_win32(ico_path: str):
    try:
        hwnd            = ctypes.windll.user32.GetForegroundWindow()
        IMAGE_ICON      = 1
        LR_LOADFROMFILE = 0x00000010
        WM_SETICON      = 0x0080
        ICON_SMALL      = 0
        ICON_BIG        = 1
        h16  = ctypes.windll.user32.LoadImageW(None, ico_path, IMAGE_ICON, 16,  16,  LR_LOADFROMFILE)
        h256 = ctypes.windll.user32.LoadImageW(None, ico_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
        if h16:  ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h16)
        if h256: ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG,   h256)
    except Exception as e:
        print(f"[icon] {e}")


def main():
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("naavos.app.1")

    bp       = base_path()
    ico_path = bp / "icon.ico"

    # Читаем index.html и запускаем локальный сервер
    html     = (bp / "index.html").read_bytes()
    port     = find_free_port()
    start_server(html, port)

    bridge = Bridge()

    window = webview.create_window(
        title="На авось",
        url=f"http://127.0.0.1:{port}/",
        js_api=bridge,
        width=1300,
        height=860,
        min_size=(960, 640),
        resizable=True,
        text_select=True,
        confirm_close=False,
        background_color="#0d0d0f",
    )

    def on_shown():
        if sys.platform == "win32" and ico_path.exists():
            set_icons_win32(str(ico_path))

    window.events.shown += on_shown

    if sys.platform == "win32":
        webview.start(gui="edgechromium", debug=False)
    elif sys.platform == "darwin":
        webview.start(gui="cocoa", debug=False)
    else:
        webview.start(gui="gtk", debug=False)


if __name__ == "__main__":
    main()
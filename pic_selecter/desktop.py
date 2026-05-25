from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DesktopConfig:
    host: str = "127.0.0.1"
    port: int = 0
    title: str = "片刻"
    width: int = 1480
    height: int = 980
    min_width: int = 1180
    min_height: int = 760


class BackgroundServer:
    def __init__(self, flask_app: Any, host: str, port: int):
        self.flask_app = flask_app
        self.host = host
        self.port = port
        self._server = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        from werkzeug.serving import make_server

        self._server = make_server(self.host, self.port, self.flask_app, threaded=True)
        self.port = int(self._server.server_port)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="pianke-desktop-server",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.shutdown()
            except Exception:
                pass
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None


def pick_port(host: str = "127.0.0.1", preferred: int = 0) -> int:
    if preferred > 0:
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def wait_until_listening(host: str, port: int, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"桌面服务启动超时：{host}:{port}")


def launch_desktop_app(flask_app: Any, config: DesktopConfig) -> int:
    try:
        import webview
    except Exception as exc:
        raise RuntimeError(
            "缺少桌面窗口依赖 pywebview，请先安装 requirements.txt 后重试"
        ) from exc

    server = BackgroundServer(
        flask_app=flask_app,
        host=config.host,
        port=pick_port(config.host, config.port),
    )
    server.start()
    wait_until_listening(config.host, server.port)
    url = f"http://{config.host}:{server.port}"

    try:
        window = webview.create_window(
            config.title,
            url=url,
            width=config.width,
            height=config.height,
            min_size=(config.min_width, config.min_height),
            text_select=True,
        )

        def _shutdown() -> None:
            server.stop()

        window.events.closed += _shutdown
        webview.start(debug=False)
        return 0
    finally:
        server.stop()

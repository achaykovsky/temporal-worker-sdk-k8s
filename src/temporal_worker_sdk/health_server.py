"""Optional threaded HTTP server: /livez, /readyz, /metrics."""

from __future__ import annotations

import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import urlparse

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)


def parse_bind_addr(addr: str) -> tuple[str, int]:
    """Parse ``host:port`` (host may be ``0.0.0.0``)."""
    parsed = urlparse(f"//{addr}" if "://" not in addr else addr)
    host = parsed.hostname
    port = parsed.port
    if host is None or port is None:
        # host:port without scheme
        if ":" not in addr:
            raise ValueError(f"Invalid bind address {addr!r}; expected host:port")
        host_part, _, port_part = addr.rpartition(":")
        if not host_part or not port_part.isdigit():
            raise ValueError(f"Invalid bind address {addr!r}; expected host:port")
        return host_part, int(port_part)
    return host, port


class HealthMetricsServer:
    """Serves liveness, readiness, and Prometheus metrics on one bind address."""

    def __init__(
        self,
        bind_addr: str,
        registry: CollectorRegistry,
        *,
        is_live: Callable[[], bool],
        is_ready: Callable[[], bool],
    ) -> None:
        host, port = parse_bind_addr(bind_addr)
        self._host = host
        self._port = port
        self._registry = registry
        self._is_live = is_live
        self._is_ready = is_ready
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        parent = self

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: object) -> None:
                logger.debug("health_http %s", fmt % args)

            def do_GET(self) -> None:
                path = urlparse(self.path).path.rstrip("/") or "/"
                if path == "/livez":
                    code = 200 if parent._is_live() else 503
                    body = b"ok\n" if code == 200 else b"not live\n"
                elif path == "/readyz":
                    code = 200 if parent._is_ready() else 503
                    body = b"ready\n" if code == 200 else b"not ready\n"
                elif path == "/metrics":
                    data = generate_latest(parent._registry)
                    self.send_response(200)
                    self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                else:
                    self.send_error(404, "Not Found")
                    return

                self.send_response(code)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self._httpd = ThreadingHTTPServer((self._host, self._port), _Handler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="temporal-worker-health",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Health and metrics HTTP listening on %s:%s (/livez /readyz /metrics)",
            self._host,
            self._port,
        )

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

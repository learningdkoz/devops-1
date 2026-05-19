# Мини-HTTP-сервер на stdlib — чтобы не тащить fastapi/uvicorn ради демки.
# Достаточно для smoke/health-чеков, k6, DAST-сканов и Helm-probes.
from __future__ import annotations

import json
import logging
import os
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app import __version__
from app.greeter import greet

log = logging.getLogger("app.server")


class Handler(BaseHTTPRequestHandler):
    # Стандартный лог BaseHTTPServer пишет в stderr — заворачиваем в logging,
    # чтобы попадало в общий пайплайн логов (Loki/ELK).
    def log_message(self, fmt: str, *args: object) -> None:
        log.info("%s - %s", self.address_string(), fmt % args)

    def _json(self, code: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 — имя метода диктует BaseHTTPRequestHandler
        if self.path in ("/health", "/healthz", "/livez"):
            # Простейшая liveness — сервис жив, отвечает.
            self._json(200, {"status": "ok"})
            return
        if self.path == "/readyz":
            # Readiness — отдельно от liveness, мало ли понадобится прогревать кеш.
            self._json(200, {"status": "ready"})
            return
        if self.path == "/version":
            # Версия нужна для smoke-тестов после деплоя.
            self._json(200, {"version": __version__})
            return
        if self.path.startswith("/hi"):
            # /hi?name=World — основная «бизнес»-ручка.
            from urllib.parse import parse_qs, urlparse

            # keep_blank_values — иначе пустое name= не попадёт в qs и мы не
            # сможем отличить «не передал» от «передал пустое».
            qs = parse_qs(urlparse(self.path).query, keep_blank_values=True)
            name = (qs.get("name") or ["PyCharm"])[0]
            try:
                self._json(200, {"message": greet(name)})
            except ValueError as e:
                self._json(400, {"error": str(e)})
            return
        self._json(404, {"error": "not found"})


def run(host: str = "0.0.0.0", port: int | None = None) -> None:
    # Порт берём из ENV — так удобнее переопределять в k8s/docker.
    port = port or int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)

    def _graceful(_sig, _frm):  # type: ignore[no-untyped-def]
        # Грейсфул-шатдаун — без него k8s будет резать соединения по SIGTERM.
        log.info("got signal, shutting down")
        server.shutdown()

    signal.signal(signal.SIGTERM, _graceful)
    signal.signal(signal.SIGINT, _graceful)

    log.info("listening on %s:%s (v%s)", host, port, __version__)
    server.serve_forever()


def main() -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

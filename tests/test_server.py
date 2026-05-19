# Интеграционные тесты HTTP-ручек (in-process) — отрабатывают CDL-06.
# Поднимаем сервер в отдельном треде и стучимся через http.client.
from __future__ import annotations

import http.client
import threading
import time

import pytest

from app.server import Handler, ThreadingHTTPServer


@pytest.fixture(scope="module")
def server():
    # Порт 0 — пусть ядро само выберет свободный, чтобы CI не падал из-за занятых портов.
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    # Микро-задержка, чтобы поток успел встать.
    time.sleep(0.05)
    yield port
    srv.shutdown()
    th.join(timeout=2)


def _get(port: int, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return resp.status, body


def test_health(server):
    code, body = _get(server, "/health")
    assert code == 200
    assert "ok" in body


def test_ready(server):
    code, body = _get(server, "/readyz")
    assert code == 200
    assert "ready" in body


def test_version(server):
    code, body = _get(server, "/version")
    assert code == 200
    assert "version" in body


def test_hi_default(server):
    code, body = _get(server, "/hi")
    assert code == 200
    assert "Hi, PyCharm" in body


def test_hi_named(server):
    code, body = _get(server, "/hi?name=World")
    assert code == 200
    assert "Hi, World" in body


def test_hi_bad_input(server):
    code, body = _get(server, "/hi?name=")
    # Пустое имя — 400, бизнес-логика бракует.
    assert code == 400
    assert "error" in body


def test_404(server):
    code, _ = _get(server, "/nope")
    assert code == 404

#!/usr/bin/env bash
# Smoke-тесты для staging (CDL-05) и прода (CDP-14).
# Дёргаем базовые ручки, валидируем коды и тело ответа.
set -euo pipefail

BASE="${1:-http://localhost:8080}"
echo "smoke against $BASE"

check() {
    local path="$1" expected="$2" needle="$3"
    local resp code body
    resp=$(curl -s -o /tmp/body -w '%{http_code}' "$BASE$path")
    code="$resp"
    body=$(cat /tmp/body)
    if [ "$code" != "$expected" ]; then
        echo "FAIL $path: expected $expected, got $code"; exit 1
    fi
    if [ -n "$needle" ] && ! grep -q "$needle" /tmp/body; then
        echo "FAIL $path: body doesn't contain '$needle'"; echo "$body"; exit 1
    fi
    echo "OK   $path -> $code"
}

check /healthz 200 ok
check /readyz  200 ready
check /version 200 version
check /hi      200 "Hi, PyCharm"
check /hi?name=World 200 "Hi, World"
check /nope    404 "not found"

echo "smoke passed"

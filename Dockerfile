# syntax=docker/dockerfile:1.7
# Multi-stage: на build-этапе ставим зависимости, на runtime — берём минимальный slim.
# Сделано так, чтобы пройти CI-14 (hadolint), CI-16 (Trivy) и CI-17 (image size).

ARG PYTHON_VERSION=3.11

# ── builder ──────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS builder
WORKDIR /build

# Без буферизации stdout и без .pyc мусора в образе.
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml ./
COPY app ./app
COPY README.md ./

# Ставим в отдельный префикс — позже его cкопируем как есть в runtime.
RUN pip install --prefix=/install .

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

# Не-root юзер — обязательное условие для CI-20 (kube-score) и общей безопасности.
RUN groupadd --system app && useradd --system --gid app --home /app --shell /usr/sbin/nologin app

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Тянем только то, что реально нужно в рантайме — без apt-кэша и dev-инструментов.
COPY --from=builder /install /usr/local

USER app
EXPOSE 8080

# Healthcheck для docker run / compose. В k8s своя probe в Helm-чарте.
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys;\
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2).status==200 else 1)"

ENTRYPOINT ["devops-demo"]

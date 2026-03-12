# ============================================
# Stage 1: Build dependencies
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Stage 2: Production image
# ============================================
FROM python:3.12-slim AS production

ARG APP_VERSION=0.1.0
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

ENV APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT} \
    BUILD_DATE=${BUILD_DATE} \
    PORT=8080 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

LABEL org.opencontainers.image.title="gitops-pipeline" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.source="https://github.com/Vinicius-Costa14/gitops-pipeline" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY main.py .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

ENTRYPOINT ["gunicorn", "main:app"]
CMD ["--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-"]

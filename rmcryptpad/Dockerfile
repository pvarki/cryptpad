FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY docker /app/docker

RUN useradd --create-home --shell /usr/sbin/nologin --uid 4001 rmcryptpad \
    && pip install --no-cache-dir .

USER rmcryptpad

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["rmcryptpad"]

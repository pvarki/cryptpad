FROM node:20-bookworm-slim AS ui-builder

WORKDIR /build/rmcryptpad/ui

COPY rmcryptpad/ui/package.json rmcryptpad/ui/pnpm-lock.yaml ./
RUN npm install -g pnpm@10 \
    && pnpm install --frozen-lockfile

COPY rmcryptpad/ui/ ./
RUN pnpm build

FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY docker /app/docker
COPY --from=ui-builder /build/rmcryptpad/ui/dist /opt/ui/cryptpad

RUN useradd --create-home --shell /usr/sbin/nologin --uid 4001 rmcryptpad \
    && pip install --no-cache-dir .

USER rmcryptpad

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["rmcryptpad"]

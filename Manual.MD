# CryptPad Local Setup Manual

## Goal

Build a fully local CryptPad deployment that follows the official two-origin installation model closely enough to validate it before we fold it into a larger Docker Compose stack.

## Installation

```bash
printf 'CPAD_UID=%s\nCPAD_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
docker compose ps
docker compose logs --no-color cryptpad
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://sandbox.cryptpad.localhost:8443
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443/checkup/
```

## Fixed Decisions

- Local mode uses `https://cryptpad.localhost:8443` as the main origin.
- Local mode uses `https://sandbox.cryptpad.localhost:8443` as the sandbox origin.
- Nginx terminates TLS and proxies both HTTP traffic and `/cryptpad_websocket`.
- CryptPad runs in Docker with persistent bind-mounted data directories.
- Local TLS uses a self-signed certificate generated automatically on first start.

## Current Status

- [x] Read the official install documentation and upstream Docker/Nginx examples.
- [x] Choose the local-domain strategy.
- [x] Write the design note and implementation plan.
- [x] Create the Docker Compose stack.
- [x] Build and boot the stack.
- [x] Verify HTTPS, proxying, and CryptPad startup.
- [x] Capture the onboarding and operator workflow.

## Working Rules

- Keep this file updated whenever the setup, commands, or verification status changes.
- Keep the stack aligned with the official install guidance where practical.
- Favor pinned slim images, non-root runtime where possible, and internal-only service exposure.

## Planned File Layout

- `compose.yaml`
- `config/config.js`
- `customize/application_config.js`
- `docker/cryptpad/`
- `docker/nginx/`
- `docker/scripts/`
- `volumes/`

## Expected Local Workflow

1. Run `docker compose up -d --build`.
2. Open `https://cryptpad.localhost:8443`.
3. Accept the local certificate warning.
4. Check `docker compose logs cryptpad` for the onboarding URL.
5. Visit `https://cryptpad.localhost:8443/checkup/` after startup.

## Verified State

- `docker compose config` passes.
- `docker compose up -d --build` succeeds.
- `docker compose ps` shows `cryptpad` healthy and `nginx` running.
- `curl -kI https://cryptpad.localhost:8443` returns `HTTP/2 200`.
- `curl -kI https://sandbox.cryptpad.localhost:8443` returns `HTTP/2 200`.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443` succeeds.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://sandbox.cryptpad.localhost:8443` succeeds.
- The generated certificate contains both SANs:
  - `DNS:cryptpad.localhost`
  - `DNS:sandbox.cryptpad.localhost`
- `curl -kI https://cryptpad.localhost:8443/checkup/` returns `HTTP/2 200`.

## Onboarding URL

Fetch the current install URL for the active data set with:

```bash
docker compose logs cryptpad
```

## Known Local Notes

- The stack uses a self-signed certificate generated automatically into `volumes/nginx/certs/`.
- Browsers will warn about the certificate until you accept it or trust the local cert manually.
- With the self-signed local setup, you may need to open both `https://cryptpad.localhost:8443` and `https://sandbox.cryptpad.localhost:8443` directly once so the browser accepts the certificate on both origins before signup and editor flows work reliably.
- The local setup records your host UID/GID in `.env` and runs the CryptPad container with that identity so the bind-mounted data stays host-accessible.
- The stack publishes only `8443` on the host. Internal CryptPad ports `3000` and `3003` stay on the Docker network.

## Troubleshooting

- If signup succeeds and then a white page appears, open `https://sandbox.cryptpad.localhost:8443/` directly, accept the certificate there too, then refresh the main site.
- If rich text shows browser-console errors but the server logs show `200` for `/pad/ckeditor-inner.html`, `/common/testworker.js`, and `/common/worker.bundle.min.js`, test again in a clean browser profile or incognito window with extensions disabled.
- `contentInt.js` console messages are not part of the CryptPad codebase in this setup and likely come from a browser extension.

## Next Step

Complete the browser onboarding flow with the install URL, then use this stack as the local base for the larger Compose integration.

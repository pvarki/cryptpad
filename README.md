# Local CryptPad

This project brings up a fully local CryptPad stack with Docker Compose using the recommended two-origin model:

- `https://cryptpad.localhost:8443`
- `https://sandbox.cryptpad.localhost:8443`

The stack uses Nginx for HTTPS and websocket proxying and generates a self-signed local certificate on first boot.

## Start

```bash
printf 'CPAD_UID=%s\nCPAD_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
```

Check the running services:

```bash
docker compose ps
```

## Open

```text
https://cryptpad.localhost:8443
https://sandbox.cryptpad.localhost:8443
```

Your browser will warn about the local self-signed certificate. Accept the warning to continue local testing.

If you want command-line certificate validation without `-k`, use the generated local cert:

```bash
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://sandbox.cryptpad.localhost:8443
```

## First-run checks

Get the onboarding URL from the CryptPad logs:

```bash
docker compose logs cryptpad
```

After the instance is up, run the diagnostics page:

```text
https://cryptpad.localhost:8443/checkup/
```

## Operator notes

The living setup runbook is in `Manual.MD`.

## Current State

At the moment this stack is up locally and responding on both origins. To get the current first-admin onboarding URL for the active data set, run:

```bash
docker compose logs --no-color cryptpad
```

#!/bin/sh
set -eu

CPAD_CONF="${CPAD_CONF:-/cryptpad/config/config.js}"

if [ ! -f "$CPAD_CONF" ]; then
  echo "CryptPad config missing at $CPAD_CONF, copying the upstream example." >&2
  cp /cryptpad/config/config.example.js "$CPAD_CONF"
fi

exec "$@"


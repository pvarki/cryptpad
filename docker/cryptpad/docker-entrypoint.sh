#!/bin/sh
set -eu

CPAD_CONF="${CPAD_CONF:-/cryptpad/config/config.js}"
CPAD_EXTRA_CA_TARGET="${NODE_EXTRA_CA_CERTS:-/tmp/cryptpad-extra-ca.pem}"

if [ -n "${NODE_EXTRA_CA_CERTS:-}" ]; then
  found_extra_ca=0
  : > "$CPAD_EXTRA_CA_TARGET"
  for cert in /ca_public/miniwerk_ca.pem /ca_public/ca_chain.pem; do
    if [ ! -f "$cert" ]; then
      continue
    fi
    cat "$cert" >> "$CPAD_EXTRA_CA_TARGET"
    printf '\n' >> "$CPAD_EXTRA_CA_TARGET"
    found_extra_ca=1
  done
  if [ "$found_extra_ca" -eq 0 ]; then
    rm -f "$CPAD_EXTRA_CA_TARGET"
    unset NODE_EXTRA_CA_CERTS
  fi
fi

if [ ! -f "$CPAD_CONF" ]; then
  echo "CryptPad config missing at $CPAD_CONF, copying the upstream example." >&2
  cp /cryptpad/config/config.example.js "$CPAD_CONF"
fi

exec "$@"

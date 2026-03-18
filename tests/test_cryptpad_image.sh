#!/bin/sh
set -eu

IMAGE_TAG="local/cryptpad-sso-test"

docker build -f docker/cryptpad/Dockerfile -t "${IMAGE_TAG}" .
docker run --rm "${IMAGE_TAG}" sh -lc '
  test -d /cryptpad/lib/plugins/sso &&
  test -f /cryptpad/config/sso.js
'

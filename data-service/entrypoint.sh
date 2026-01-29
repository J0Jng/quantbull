#!/usr/bin/env sh
set -eu

# Ensure static dirs exist and are writable for the app user.
mkdir -p /app/static/videos /app/static/video_covers
chown -R appuser:appuser /app/static || true

# Run the given CMD as appuser (container may start as root for volume permission fix).
exec su -s /bin/sh appuser -c "$*"

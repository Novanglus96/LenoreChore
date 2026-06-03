#!/bin/sh
# Conditionally start the Redis bundled in the single-container image.
#
# The app defaults REDIS_URL to redis://localhost:6379/0 (the bundled
# instance). When the operator points REDIS_URL at their own Redis server,
# the bundled instance is redundant, so we skip starting it. Exiting 0 here
# (with autorestart=unexpected in supervisord) marks this program EXITED
# without triggering a restart loop, so no idle process lingers.

case "${REDIS_URL:-}" in
  "" | redis://localhost:* | redis://127.0.0.1:* | rediss://localhost:* | rediss://127.0.0.1:*)
    echo "No external REDIS_URL configured; starting bundled Redis."
    exec redis-server --daemonize no --bind 127.0.0.1
    ;;
  *)
    echo "External REDIS_URL configured; bundled Redis not started."
    exit 0
    ;;
esac

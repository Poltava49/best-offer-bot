#!/bin/sh
set -e

Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

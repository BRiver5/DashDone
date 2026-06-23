#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
if [ -f .env ]; then set -a; source .env; set +a; fi
uvicorn main:app --reload --host 0.0.0.0 --port 8000

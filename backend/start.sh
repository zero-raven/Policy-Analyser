#!/usr/bin/env bash
uvicorn backend_fastapi:app --host 0.0.0.0 --port $PORT

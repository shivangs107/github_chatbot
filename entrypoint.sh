#!/bin/sh
if [ -z "$SERVICE_TYPE" ]; then
  echo "ERROR: SERVICE_TYPE environment variable not set"
  exit 1
fi

case "$SERVICE_TYPE" in
  api)
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;
  bot)
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
      echo "ERROR: TELEGRAM_BOT_TOKEN not set"
      exit 1
    fi
    exec python bot.py
    ;;
  *)
    echo "Unknown service type: $SERVICE_TYPE"
    exit 1
    ;;
esac
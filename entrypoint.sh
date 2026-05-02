#!/bin/sh
# Initialize the energon ledger on first boot (Fly.io volume may be empty)
mkdir -p /data
if [ ! -f "$LEDGER_PATH" ]; then
  echo '{"sealed_kwh":8025803600.512696,"batches":[],"pending_kwh":0,"last_updated":"2026-04-30T00:00:00Z"}' > "$LEDGER_PATH"
  echo "[dwallstreet] Ledger initialized at $LEDGER_PATH"
fi
exec "$@"

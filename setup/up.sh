#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF="${HERE}/../issacsim/isaacsim_5.1.sif"

# Host folders relative to current dir
CACHE_HOST="${HERE}/cache"
LOGS_HOST="${HERE}/logs"
OV_HOST="${HERE}/ov"

# Extra bind
USERDATA_HOST="/data/user_data/yjangir/yash"
USERDATA_CONT="/workspace"

mkdir -p "$CACHE_HOST" "$LOGS_HOST" "$OV_HOST"

if [[ ! -f "$SIF" ]]; then
  echo "ERROR: Could not find container: $SIF"
  echo "Make sure isaacsim_5.1.sif is in: $HERE"
  exit 1
fi

echo "=== Host GPU check ==="
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -n 20 || echo "nvidia-smi not available on host"

echo
echo "=== Launching apptainer shell ==="
echo "Dir:      $HERE"
echo "SIF:      $SIF"
echo "Binds:"
echo "  $CACHE_HOST -> /root/.cache"
echo "  $LOGS_HOST  -> /root/.nvidia-omniverse/logs"
echo "  $OV_HOST    -> /root/.local/share/ov"
echo "  $USERDATA_HOST -> $USERDATA_CONT"
echo

apptainer shell --nv \
  --bind "${CACHE_HOST}:/root/.cache" \
  --bind "${LOGS_HOST}:/root/.nvidia-omniverse/logs" \
  --bind "${OV_HOST}:/root/.local/share/ov" \
  --bind "${USERDATA_HOST}:${USERDATA_CONT}" \
  "$SIF" \
  -c 'echo "=== Container GPU check ==="; nvidia-smi | head -n 20 || echo "nvidia-smi failed (likely not on a GPU node)"; echo; exec bash -l'

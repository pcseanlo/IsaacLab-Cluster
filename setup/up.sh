#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF="${HERE}/isaac-lab-2.3.0.sif"

# Extra bind
USERDATA_HOST="${HERE}/project"
USERDATA_CONT="/workspace/project"

if [[ ! -f "$SIF" ]]; then
  echo "ERROR: Could not find container: $SIF"
  echo "Make sure isaac-lab-2.3.0.sif is in: $HERE"
  exit 1
fi

echo "=== Host GPU check ==="
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -n 20 || echo "nvidia-smi not available on host"

echo
echo "=== Launching apptainer shell ==="
echo "Dir:      $HERE"
echo "SIF:      $SIF"
echo "Binds:"
echo "  $USERDATA_HOST -> $USERDATA_CONT"

apptainer shell --nv \
  --env "ACCEPT_EULA=Y" \
  --env "PRIVACY_CONSENT=Y" \
  --no-home \
  -B $(pwd)/project:/workspace/project \
  -B $(pwd)/isaac_cache/kit:/isaac-sim/kit/cache \
  -B $(pwd)/isaac_cache/kit_data:/isaac-sim/kit/data \
  -B $(pwd)/isaac_cache/ov:/root/.cache/ov \
  -B $(pwd)/isaac_cache/pip:/root/.cache/pip \
  -B $(pwd)/isaac_cache/glcache:/root/.cache/nvidia/GLCache \
  -B $(pwd)/isaac_cache/computecache:/root/.nv/ComputeCache \
  -B $(pwd)/isaac_cache/logs:/root/.nvidia-omniverse/logs \
  -B $(pwd)/isaac_cache/data:/root/.local/share/ov/data \
  -B $(pwd)/isaac_cache/documents:/root/Documents \
  "$SIF" \
  -c 'echo "=== Container GPU check ==="; nvidia-smi | head -n 20 || echo "nvidia-smi failed (likely not on a GPU node)"; echo; exec bash -l'

CONTAINER_PATH="container"
WORKING_DIR="src"

# Extra bind
USERDATA_HOST="$WORKING_DIR"
USERDATA_CONT="/workspace/project"

SIF="$CONTAINER_PATH/isaac-lab-2.3.0.sif"

if [[ ! -f "$SIF" ]]; then
  echo "ERROR: Could not find container: $SIF"
  echo "Make sure isaac-lab-2.3.0.sif is in: $CONTAINER_PATH"
  exit 1
fi

echo "=== Host GPU check ==="
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -n 20 || echo "nvidia-smi not available on host"

echo
echo "=== Launching apptainer shell ==="
echo "Dir:      $(pwd)"
echo "SIF:      $SIF"
echo "Binds:"
echo "  $USERDATA_HOST -> $USERDATA_CONT"

apptainer shell --nv \
  --env "ACCEPT_EULA=Y" \
  --env "PRIVACY_CONSENT=Y" \
  --no-home \
  -B $WORKING_DIR:/workspace/project \
  -B $CONTAINER_PATH/isaac_cache/kit:/isaac-sim/kit/cache \
  -B $CONTAINER_PATH/isaac_cache/kit_data:/isaac-sim/kit/data \
  -B $CONTAINER_PATH/isaac_cache/ov:/root/.cache/ov \
  -B $CONTAINER_PATH/isaac_cache/pip:/root/.cache/pip \
  -B $CONTAINER_PATH/isaac_cache/glcache:/root/.cache/nvidia/GLCache \
  -B $CONTAINER_PATH/isaac_cache/computecache:/root/.nv/ComputeCache \
  -B $CONTAINER_PATH/isaac_cache/logs:/root/.nvidia-omniverse/logs \
  -B $CONTAINER_PATH/isaac_cache/data:/root/.local/share/ov/data \
  -B $CONTAINER_PATH/isaac_cache/documents:/root/Documents \
  "$SIF" \
  -c 'echo "=== Container GPU check ==="; nvidia-smi | head -n 20 || echo "nvidia-smi failed (likely not on a GPU node)"; echo; exec bash -l'

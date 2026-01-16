CONTAINER_PATH="container"
WORKING_DIR="src"

apptainer exec --nv \
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
  "$CONTAINER_PATH/isaac-lab-2.3.0.sif" \
  /isaac-sim/python.sh /workspace/project/usda_test.py --enable_cameras --headless

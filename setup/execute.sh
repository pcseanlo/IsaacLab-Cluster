HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF="${HERE}/isaac-lab-2.3.0.sif"

apptainer exec --nv \
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
  /isaac-sim/python.sh /workspace/project/usda_test.py --enable_cameras --headless

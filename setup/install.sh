# Go to desire install path
mkdir container
cd container

# Use apptainer to download the image
apptainer pull isaac-lab-2.3.0.sif docker://nvcr.io/nvidia/isaac-lab:2.3.0

# Create folders for binding
mkdir -p isaac_cache/kit
mkdir -p isaac_cache/ov
mkdir -p isaac_cache/pip
mkdir -p isaac_cache/glcache
mkdir -p isaac_cache/computecache
mkdir -p isaac_cache/logs
mkdir -p isaac_cache/data
mkdir -p isaac_cache/documents
mkdir -p isaac_cache/kit_data
mkdir -p project # Place the working files under this folder

cd ..
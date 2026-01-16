# RobotArena Isaac Sim Setup

This repository contains the setup and configuration for running [RobotArena](https://github.com/simpler-env/RobotArena) with NVIDIA Isaac Sim 5.1.0 and Isaac Lab 2.3.0 using Apptainer (Singularity) containers.

## Overview

This setup provides an isolated containerized environment for running Isaac Sim, which is used for robot simulation and evaluation as part of the RobotArena benchmarking framework. The container setup ensures reproducible environments and easy deployment on HPC systems.

## Repository Structure

```
IssacSim-Cluster/
├── setup/
│   ├── install.sh          # Script to download container image
│   ├── up.sh               # Script to launch the container
│   └── execute.sh          # Script to execute the command in the container
└── README.md               # This file
```

## Prerequisites

- **Apptainer/Singularity**: Required for running containers
- **NVIDIA GPU**: Required for Isaac Sim (with CUDA support)
- **nvidia-smi**: For GPU verification
- **SLURM** (optional): If running on an HPC cluster

## Installation

### 1. Download Isaac Sim Container

Run the installation script to pull the Isaac Sim 5.1 container:

```bash
cd setup
bash install.sh
```

This will download the `isaac-lab-2.3.0.sif` container image from NVIDIA's container registry. You change the path inside the script to your deisred download location.

### 2. Verify Container

Ensure the container file exists:

```bash
ls -lh ${YOUR_DOWNLOAD_PATH}/isaac-lab-2.3.0.sif
```

## Usage

### Launching the Container

We provide 2 running scripts `setup/` directory:

```bash
bash up.sh
```

This script will:
- Check for GPU availability on the host
- Launch an Apptainer shell with:
  - GPU support (`--nv`)
  - Persistent cache bindings
  - Your workspace mounted at `/workspace/project`
  - Isaac Sim logs and Omniverse data directories

```bash
bash execute.sh
```

This script will:
- Launch an Apptainer with:
  - GPU support (`--nv`)
  - Persistent cache bindings
  - Your workspace mounted at `/workspace/project`
  - Execute the command (the last line of the scripts) inside the container

### Container Environment

Once inside the container, you'll have:
- **Working directory**: `/workspace/project` (maps to your desired binding location)


### Running Isaac Lab

Inside the container, you can run Isaac Lab applications and scripts. The container includes all necessary dependencies and CUDA libraries.

To run `python` command inside the container, please use `/isaac-sim/python.sh` for that

The `isaaclab` resource folder will be at `/workspace/isaaclab`

## Integration with RobotArena

This Isaac Sim setup is designed to work with the [RobotArena](https://github.com/simpler-env/RobotArena) benchmarking framework. The RobotArena project provides:

- Robot policy evaluation environments
- Support for multiple models (CogAct, RoboVLM, Octo, SpatialVLA)
- Real-to-sim translation capabilities
- Custom simulation environments

To use this setup with RobotArena:

1. Clone the RobotArena repository to your workspace
2. Launch this container using `setup/up.sh`
3. Navigate to your RobotArena directory inside the container
4. Follow RobotArena's setup instructions for Isaac Sim integration

## Configuration

### Environment Variables

The container inherits your host environment. Key variables that may be useful:

- `APPTAINER_TMPDIR`: Set to `/scratch` for temporary files
- `LD_LIBRARY_PATH`: Includes NVIDIA libraries
- GPU-related cache directories (see `.bashrc` for details)

### Custom Bash Configuration

Your personal `.bashrc` is available in the `setup/bashrc` file for reference. The container uses its own shell initialization, but you can source this configuration inside the container if needed:

```bash
source /workspace/robotarena_issacsim/setup/bashrc
```

This includes your aliases, conda/mamba setup, cache directory configurations, and other customizations.

## Troubleshooting

### GPU Not Detected

If `nvidia-smi` fails inside the container:
- Verify GPU is available on the host: `nvidia-smi` (outside container)
- Ensure you're on a GPU node (if using SLURM)
- Check that `--nv` flag is being used (it's included in `up.sh`)

### Container Not Found

If you see "Could not find container":
- Run `bash setup/install.sh` to download the container
- Verify the path in `up.sh` matches your directory structure

### Permission Issues

If you encounter permission errors:
- Ensure isaac_cache/ directories are writable
- Check that your user has access to the workspace directory

## Related Projects

- [RobotArena](https://github.com/simpler-env/RobotArena): Main benchmarking framework
- [SimplerEnv](https://github.com/simpler-env/SimplerEnv): Simulated manipulation environments
- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim): Official Isaac Sim documentation
- [NVIDIA Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html): Official Isaac Lab documentation

## Notes

- The container image is large (~10GB+), ensure sufficient disk space
- First launch may take time as Omniverse initializes
- Cache directories persist between container runs for faster subsequent launches

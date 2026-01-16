#!/usr/bin/env python3

import argparse
from isaaclab.app import AppLauncher

# 1. Parse Args (Standard Isaac Lab boilerplate)
#    This allows you to pass --headless or --livestream automatically
parser = argparse.ArgumentParser(description="Test Custom Scene Collision")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# 2. Launch Isaac Sim
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# -----------------------------------------------------------------------------
# Imports after app launch (CRITICAL)
# -----------------------------------------------------------------------------
import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg, RigidObjectCfg, RigidObject
from isaaclab.scene import InteractiveSceneCfg, InteractiveScene
from isaaclab.utils import configclass
from isaaclab.sensors.camera import Camera, CameraCfg
import omni.replicator.core as rep
import os
import torch
from isaaclab.utils import convert_dict_to_backend

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

@configclass
class MySceneCfg(InteractiveSceneCfg):
    """Configuration for our custom scene."""
    
    # 1. The Custom NuRec/Grut Scene (Static Background)
    background = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Gaussians",
        spawn=sim_utils.UsdFileCfg(
            # UPDATE THIS PATH TO YOUR REAL FILE
            usd_path="/workspace/project/assets/usda_data/default.usda",
            scale=(1.0, 1.0, 1.0),
            # Rigid props must be enabled even for static objects if we want collision
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                rigid_body_enabled=True,
                kinematic_enabled=True,   # True = Static (won't fall)
                disable_gravity=True,
            ),
            # Collision must be enabled explicitly
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 1.0, 0.0)),  # w,x,y,z
    )

    light = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Light",
        spawn=sim_utils.DistantLightCfg(intensity=5000.0, color=(1.0, 1.0, 1.0))
    )

    point_light = AssetBaseCfg(
        prim_path="/World/PointLight",
        spawn=sim_utils.SphereLightCfg(
            radius=0.5,        # Make the "bulb" visible (50cm)
            intensity=50000.0, # CRITICAL: Needs to be huge (Lumens)
            color=(1.0, 0.9, 0.8) # Warm light
        ),
        init_state=AssetBaseCfg.InitialStateCfg(
            # MOVE IT UP! 
            # If your object is at 0,0,0, put the light at z=3.0 meters
            pos=(0.0, 0.0, 0.0) 
        )
    )

    # 2. The Test Cube (Dynamic Object)
    test_cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/TestCube",
        spawn=sim_utils.CuboidCfg(
            size=(0.05, 0.05, 0.05), # 50cm cube
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)), # Red
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                rigid_body_enabled=True,
                disable_gravity=False
            ),
            mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.5, 0.03)), # Drop from 2m high
    )

    collider = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Collider",
        spawn=sim_utils.UsdFileCfg(
            usd_path="/workspace/project/assets/collider_triangle/collider.usd",
            scale=(1.0, 1.0, 1.0),
            # Enable physics on the GLB so it actually acts as a wall
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                rigid_body_enabled=True,
                kinematic_enabled=True, # Static
                disable_gravity=True,
            ),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
        ),
        # Rotate -90 on X (standard GLB fix)
        init_state=AssetBaseCfg.InitialStateCfg(rot=(0.707, -0.707, 0.0, 0.0))
    )

    camera1 = CameraCfg(
        prim_path="{ENV_REGEX_NS}/CameraSensor1",
        update_period=0,
        height=480,
        width=640,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0,
            focus_distance=400.0,
            vertical_aperture=20.955,
            horizontal_aperture=20.955 * (640 / 480),
            clipping_range=(0.1, 1.0e3)
        )
    )

    camera2 = CameraCfg(
        prim_path="{ENV_REGEX_NS}/CameraSensor2",
        update_period=0,
        height=480,
        width=640,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0,
            focus_distance=400.0,
            vertical_aperture=20.955,
            horizontal_aperture=20.955 * (640 / 480),
            clipping_range=(0.1, 1.0e3)
        )
    )

    camera3 = CameraCfg(
        prim_path="{ENV_REGEX_NS}/CameraSensor3",
        update_period=0,
        height=480,
        width=640,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0,
            focus_distance=400.0,
            vertical_aperture=20.955,
            horizontal_aperture=20.955 * (640 / 480),
            clipping_range=(0.1, 1.0e3)
        )
    )

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------
def main():
    # 1. Setup Simulation Context
    sim_cfg = sim_utils.SimulationCfg(dt=1.0 / 60.0, device=args_cli.device)
    sim = sim_utils.SimulationContext(sim_cfg)
    
    # Set camera view to see the action
    # sim.set_camera_view(eye=[5.0, 5.0, 5.0], target=[0.0, 0.0, 0.0])

    # 2. Setup the Scene
    # Isaac Lab uses a regex namespace {ENV_REGEX_NS} to support cloning environments.
    # We create 1 environment at origin.
    scene_cfg = MySceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)

    stage = sim.stage

    # ... inside main(), after sim.reset() ...

    print("-" * 50)
    print("DEBUG: SEARCHING FOR TARGET PRIMS")
    
    found_any = False
    for prim in sim.stage.Traverse():
        path = prim.GetPath().pathString
        # Check if 'Gaussian' or 'Collider' is part of the path name
        if "Gaussians" in path or "Collider" in path:
            print(f"FOUND: {path}")
            found_any = True
            
    if not found_any:
        print("RESULT: No prims found matching 'Gaussians' or 'Collider'.")
        
    print("-" * 50)

    # 2. Get the Prim objects
    # Note: Using /World/Gaussian because we have 1 env at origin
    gaussian_prim_path = "/World/envs/env_0/Gaussians" 
    collider_prim_path = "/World/envs/env_0/Collider"
    
    gaussian_prim = stage.GetPrimAtPath(gaussian_prim_path)
    
    if gaussian_prim.IsValid():
        print(f"[INFO] Found Gaussian Prim at: {gaussian_prim_path}")
        
        # 3. Create or Get the 'proxy' relationship
        # This corresponds to "Raw USD Properties -> proxy"
        proxy_rel = gaussian_prim.CreateRelationship("proxy", custom=False)
        
        # 4. Add the Target (Clicking "Add Target")
        from pxr import Sdf
        proxy_rel.AddTarget(Sdf.Path(collider_prim_path))
        print(f"[INFO] Successfully linked proxy target to: {collider_prim_path}")
        
        # Optional: Often when you link a proxy, you want to hide the proxy mesh itself
        # so you only see the Gaussian but hit the mesh.
        import isaacsim.core.utils.prims as prim_utils
        collider_prim = stage.GetPrimAtPath(collider_prim_path)
        prim_utils.set_prim_visibility(collider_prim, False)
        
    else:
        print("[ERROR] Could not find Gaussian prim!")

    base_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Writer for Camera 1
    output_dir_1 = os.path.join(base_dir, "output", "cam_test", "cam1")
    os.makedirs(output_dir_1, exist_ok=True)
    rep_writer1 = rep.BasicWriter(output_dir=output_dir_1, frame_padding=4)

    # Writer for Camera 2
    output_dir_2 = os.path.join(base_dir, "output", "cam_test", "cam2")
    os.makedirs(output_dir_2, exist_ok=True)
    rep_writer2 = rep.BasicWriter(output_dir=output_dir_2, frame_padding=4)

    # Writer for Camera 3
    output_dir_3 = os.path.join(base_dir, "output", "cam_test", "cam3")
    os.makedirs(output_dir_3, exist_ok=True)
    rep_writer3 = rep.BasicWriter(output_dir=output_dir_3, frame_padding=4)

    print(f"[INFO] Images will be saved to: {output_dir_1} and {output_dir_2}")

    # 3. Reset Simulation
    print("[INFO] Resetting simulation...")
    sim.reset()
    
    print("[INFO] Simulation running. Cube should fall and land on the scene.")

    camera = scene["camera1"]

    camera_positions = torch.tensor([[0, 0, 0]], device=sim.device, dtype=torch.float32)
    # camera_positions = torch.tensor([scene_entities["pose"][0], [-0.1, 0.0, 0.0]], device=sim.device)
    camera_targets = torch.tensor([[0.5, 0.5, -0.5]], device=sim.device, dtype=torch.float32)
    # These orientations are in ROS-convention, and will position the cameras to view the origin

    # Set pose: There are two ways to set the pose of the camera.
    # -- Option-1: Set pose using view
    camera.set_world_poses_from_view(camera_positions, camera_targets)

    camera2 = scene["camera2"]
    camera2_positions = torch.tensor([[-0.5, -0.5, 0.5]], device=sim.device, dtype=torch.float32)
    camera2_targets = torch.tensor([[0, 0, 0]], device=sim.device, dtype=torch.float32)
    camera2.set_world_poses_from_view(camera2_positions, camera2_targets)

    camera3 = scene["camera3"]
    camera3_positions = torch.tensor([[2.5, 2.5, 2.5]], device=sim.device, dtype=torch.float32)
    camera3_targets = torch.tensor([[0, 0, 0]], device=sim.device, dtype=torch.float32)
    camera3.set_world_poses_from_view(camera3_positions, camera3_targets)

    # 4. Main Loop
    step = 0
    while simulation_app.is_running():
        if step > 100:
            print("[INFO] Finished simulation.")
            break
        print("[INFO] Step:", step)
        # Step physics
        sim.step()
        step += 1
        
        # Update scene buffers (required for RigidObjects to sync physics)
        scene.update(dt=sim.get_physics_dt())
        
        for cam, rep_writer in zip([camera, camera2, camera3], [rep_writer1, rep_writer2, rep_writer3]):
            if "rgb" in cam.data.output.keys():
                camera_index = 0  # Since we have only 1 env
                # Get data
                single_cam_data = convert_dict_to_backend(
                    {k: v[camera_index] for k, v in cam.data.output.items()}, backend="numpy"
                )
                
                # Extract the other information
                single_cam_info = cam.data.info[camera_index]

                # Pack data back into replicator format to save them using its writer
                rep_output = {"annotators": {}}
                for key, data, info in zip(single_cam_data.keys(), single_cam_data.values(), single_cam_info.values()):
                    if key != "rgb" and "seg" not in key: continue
                    # print(f"[DEBUG] Preparing data for key: {key}, info: {info}")
                    if info is not None:
                        rep_output["annotators"][key] = {"render_product": {"data": data, **info}}
                    else:
                        rep_output["annotators"][key] = {"render_product": {"data": data}}
                # Save images
                # Note: We need to provide On-time data for Replicator to save the images.
                rep_output["trigger_outputs"] = {"on_time": camera.frame[camera_index]}
                print(f"[INFO] Saving data from camera index {camera_index} at frame {camera.frame[camera_index]}...")
                print(f"rep_output keys: {rep_output['annotators'].keys()}")
                rep_writer.write(rep_output)


if __name__ == "__main__":
    main()
    simulation_app.close()
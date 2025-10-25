# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from isaacsim import SimulationApp


CONFIG = {
    "width": 1920,
    "height": 1080,
    "window_width": 1920,
    "window_height": 1080,
    "headless": True,
    "hide_ui": False,  # Show the GUI
    "renderer": "RayTracedLighting",
    "display_options": 3286,  # Set display options to show default grid
    "multi_gpu":False,
    }

kit = SimulationApp(launch_config=CONFIG)

# Enable WebRTC Livestream extension    
from omni.isaac.core.utils.extensions import enable_extension

# Default Livestream settings
kit.set_setting("/app/window/drawMouse", True)
kit.set_setting("/app/livestream/proto", "ws")
kit.set_setting("/ngx/enabled", False)
# Default URL: http://localhost:8211/streaming/webrtc-client/
# Enable Livestream extension
enable_extension("omni.services.livestream.nvcf")


# URDF import, configuration and simulation sample
# kit = SimulationApp({"renderer": "RaytracedLighting", "headless": False})
import omni.kit.commands
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.extensions import get_extension_path_from_name
from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, UsdLux, UsdPhysics
from isaacsim.core.utils.viewports import set_camera_view


from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage

import numpy as np
# from omni.isaac.core.utils.stage import create_new_stage

# # Create a new stage first
# create_new_stage()

# Setting up import configuration:
status, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
import_config.merge_fixed_joints = False
import_config.convex_decomp = False
import_config.import_inertia_tensor = True
import_config.fix_base = True
# import_config.collision_from_visuals = True
import_config.self_collision = True
import_config.distance_scale = 1.0

def set_camera_interactive():
    """
    Manually adjust camera in viewport, then run this to get the values
    """
    import omni.kit.viewport.utility as vp_utils
    from pxr import Gf
    
    viewport_api = vp_utils.get_active_viewport()
    if viewport_api:
        camera = viewport_api.stage.GetPrimAtPath(viewport_api.camera_path)
        from pxr import UsdGeom
        
        camera_xform = UsdGeom.Xformable(camera)
        matrix = camera_xform.ComputeLocalToWorldTransform(0)
        
        # Extract camera position
        eye = matrix.ExtractTranslation()
        
        print("Current camera settings:")
        print(f"eye=[{eye[0]:.2f}, {eye[1]:.2f}, {eye[2]:.2f}]")
        print("\nCopy this to your code:")
        print(f"set_camera_view(")
        print(f"    eye=[{eye[0]:.2f}, {eye[1]:.2f}, {eye[2]:.2f}],")
        print(f"    target=[0.0, 0.0, 0.5],")
        print(f"    camera_prim_path='/OmniverseKit_Persp'")
        print(f")")


set_camera_view(
    eye=[1.12, 0.82, 0.53], target=[0.00, 0.00, 0.50], camera_prim_path="/OmniverseKit_Persp"
)  # set camera view

# Get path to extension data:
extension_path = get_extension_path_from_name("isaacsim.asset.importer.urdf")
# Import URDF, prim_path contains the path the path to the usd prim in the stage.
# status, prim_path = omni.kit.commands.execute(
#     "URDFParseAndImportFile",
#     urdf_path=extension_path + "/data/urdf/robots/carter/urdf/carter.urdf",
#     import_config=import_config,
#     get_articulation_root=True,
# )
# urdf_path = extension_path + "/data/urdf/robots/ManiSkill-WidowX250S/wx250s.urdf"
# status, prim_path = omni.kit.commands.execute(
#     "URDFParseAndImportFile",
#     urdf_path=urdf_path,
#     import_config=import_config,
#     get_articulation_root=True,
# )


# urdf_path = extension_path + "/data/urdf/robots/trossen_arm_description/urdf/generated/mobile_ai.urdf"
# status, prim_path = omni.kit.commands.execute(
#     "URDFParseAndImportFile",
#     urdf_path=urdf_path,
#     import_config=import_config,
#     get_articulation_root=True,
# )


# wxai_base, wxai_follower, wxai_leader_left, wxai_leader_right
urdf_path = extension_path + "/data/urdf/robots/trossen_arm_description/urdf/generated/wxai/wxai_leader_right.urdf"
status, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=urdf_path,
    import_config=import_config,
    get_articulation_root=True,
)
# import pdb; pdb.set_trace()
import os
print(f"URDF exists: {os.path.exists(urdf_path)}")
print(f"Status: {status}, Prim path: {prim_path}")
# Get stage handle
stage = omni.usd.get_context().get_stage()

# Enable physics
scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))
# Set gravity
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
scene.CreateGravityMagnitudeAttr().Set(9.81)
# Set solver settings
PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physxSceneAPI = PhysxSchema.PhysxSceneAPI.Get(stage, "/physicsScene")
physxSceneAPI.CreateEnableCCDAttr(True)
physxSceneAPI.CreateEnableStabilizationAttr(True)
physxSceneAPI.CreateEnableGPUDynamicsAttr(False)
physxSceneAPI.CreateBroadphaseTypeAttr("MBP")
physxSceneAPI.CreateSolverTypeAttr("TGS")


# Load Isaac Sim's default grid environment (best option!)
nucleus_path = get_assets_root_path()
if nucleus_path:
    environment_path = nucleus_path + "/Isaac/Environments/Grid/default_environment.usd"
    add_reference_to_stage(environment_path, "/World/Environment")
    print("Loaded Isaac Sim default grid environment")
else:
    print("Nucleus not available, using basic setup")
    # Fall back to manual setup
    PhysicsSchemaTools.addGroundPlane(stage, "/groundPlane", "Z", 1500, 
                                      Gf.Vec3f(0, 0, 0), Gf.Vec3f(0.5))
# Add ground plane
# PhysicsSchemaTools.addGroundPlane(stage, "/groundPlane", "Z", 1500, Gf.Vec3f(0, 0, -0.25), Gf.Vec3f(0.5))

# Add lighting
distantLight = UsdLux.DistantLight.Define(stage, Sdf.Path("/DistantLight"))
distantLight.CreateIntensityAttr(500)

omni.timeline.get_timeline_interface().play()
# perform one simulation step so physics is loaded and dynamic control works.
kit.update()
# Create articulation object
robot = Articulation(prim_path)
robot.initialize()

# Get joint information
joint_names = robot.dof_names
num_joints = robot.num_dof
print(f"Robot has {num_joints} joints: {joint_names}")

# # Get default joint positions
# default_positions = robot.get_joint_positions()
# print(f"Default positions: {default_positions}")

# Simulation loop for waving
from omni.isaac.core import World

world = World()
world.reset()

# Get default positions (shape: (1, 8))
default_positions = robot.get_joint_positions()
print(f"Default positions shape: {default_positions.shape}")
print(f"Default positions: {default_positions}")

# Simulation loop for waving
sim_time = 0.0
dt = world.get_physics_dt()
# dt = 1.0 / 60.0

for i in range(1600):  # Run for ~10 seconds
    # Create waving motion - handle 2D array properly
    wave_positions = default_positions.copy()
    
    # Index as [0, joint_idx] since it's a 2D array (batch, joints)
    wave_positions[0, :] = 0.25 * np.sin(2 * np.pi * 0.5 * sim_time)  # waist
    # wave_positions[0, 1] = 0.3 * np.sin(2 * np.pi * 0.5 * sim_time)  # shoulder
    # wave_positions[0, 2] = 0.4 * np.sin(2 * np.pi * 0.5 * sim_time + np.pi/4)  # elbow
    # wave_positions[0, 4] = 0.5 * np.sin(2 * np.pi * 0.5 * sim_time + np.pi/2)  # wrist_angle
    # wave_positions[0, -2:] = 0  # grippers 
    
    # Apply joint positions
    robot.set_joint_position_targets(wave_positions)
    # set_camera_interactive()
    # Step simulation
    world.step(render=True)
    sim_time += dt
    
    if i % 60 == 0:  # Print every second
        print(f"Time: {sim_time:.1f}s")

print("Waving complete!")

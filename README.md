# Autonomous TurtleBot3 Navigation

This project implements autonomous TurtleBot3 navigation using ROS 2 Humble and Nav2 in simulation, for both a single robot and multiple robots sharing one world.

## Single-robot navigation

A single TurtleBot3 Burger navigates the standard `turtlebot3_world` using a map, AMCL localisation, and the Nav2 planning stack. The full simulation is started with one command:

```bash
pixi shell -e humble
ros2 launch project_path_planning tb3_sim_nav.launch.py   # Gazebo tb3 world + AMCL + Nav2 stack
ros2 run project_path_planning move_to_spot --ros-args \
  --params-file src/project_path_planning/config/spot-list.yaml -p spot_name:=goal
```

- Start/end poses live in `src/project_path_planning/config/spot-list.yaml` (`start` = spawn pose `-2.0, -0.5`; `goal` = free cell `0.55, 0.55`). `move_to_spot` reads `<spot_name>_x/_y/_yaw` parameters.
- AMCL initial pose is hardcoded in `amcl_config.yaml` to the Gazebo spawn pose (`set_initial_pose: true`), so no RViz "2D Pose Estimate" click is needed for the default bringup.
- Costmap config (global static+obstacle+inflation, local rolling voxel) is in `path_planning_params.yaml`, adapted from `turtlebot3_navigation2` burger params (`robot_radius: 0.105`).

The building blocks behind this launch file (mapping, localisation, and path planning) are described package by package in the sections below. The robot can also be sent on a full round trip (out to the goal and back to its start) with:

```
ros2 run multi_robot round_trip --ros-args \
  --params-file install/multi_robot/share/multi_robot/config/spots_single.yaml -p use_sim_time:=true
```

## Multi-robot navigation

The `multi_robot` package runs two TurtleBot3 Burgers in the same world, each with its **own complete Nav2 stack** (controller, planner, behaviours, and BT navigator) under its own namespace, `/tb3_0` and `/tb3_1`. There is no central coordination between the robots: each one plans with A* over the shared static map as if it were alone, and the robots only avoid each other because each local costmap observes the other robot through the laser scanner, letting the DWB local planner steer around it.

Key design points:

- **One shared TF tree with prefixed frame names.** All transforms are published on the global `/tf` topic, with each robot's frames prefixed (`tb3_0/odom`, `tb3_0/base_footprint`, ...) under a single shared `map` frame.
- **Namespaced simulation.** Each robot is spawned with `-robot_namespace`, which namespaces its topics (`/tb3_0/cmd_vel`, `/tb3_0/scan`, ...). The frame names baked into the Gazebo plugins are rewritten per robot before spawning, and one `robot_state_publisher` per robot publishes its description with a matching `frame_prefix`.
- **Shared map, per-robot localisation.** A single `map_server` serves `/map` to one AMCL instance per robot, each configured with its robot's frames, scan topic, and initial pose.
- **Per-robot Nav2 parameters.** Each robot's parameter file nests all Nav2 configuration under its namespace, with prefixed frames and absolute scan topics, so the two stacks stay fully independent.

Start the simulation (add `gui:=false` to run headless):

```
ros2 launch multi_robot multi_robot_sim.launch.py
```

Then send each robot on its round trip. The default spots make the robots swap positions and return, so they must pass each other in the arena:

```
ros2 run multi_robot round_trip --ros-args -r __ns:=/tb3_0 \
  --params-file install/multi_robot/share/multi_robot/config/spots_multi.yaml -p use_sim_time:=true
ros2 run multi_robot round_trip --ros-args -r __ns:=/tb3_1 \
  --params-file install/multi_robot/share/multi_robot/config/spots_multi.yaml -p use_sim_time:=true
```

The `round_trip` node is built on `nav2_simple_commander`. It reads `start_*` and `goal_*` poses from its parameters, navigates to the goal, and returns to the start. It is namespace-agnostic: the same executable drives the single robot (no namespace remap) or either robot in the multi-robot world.

## Packages

Autonomous navigation is split across dedicated packages: mapping, localisation (plus its service interfaces), path planning, and multi-robot simulation.

### Project Mapping

#### Using Cartographer ROS

The project mapping package is used to create and save a map of the environment. The launch file `cartographer.launch.py` launches the nodes from the `cartographer_ros` package.

Executing the `cartographer_node` with `use_sim_time: True` allows for time synchronisation in simulation. This node is used for SLAM. Configuration parameters are provided via the `cartographer.lua` file.

Additionally, the `cartographer_occupancy_grid_node` is launched and listens to the submaps published by SLAM, consuming the submaps to construct a ROS 2 occupancy_grid, which is also published. A publish period of 1.0 seconds is set, as generating the map is computationally expensive.

To launch and begin creating a map using SLAM:

```
ros2 launch project_mapping cartographer.launch.py
```

Teleoperation can be used to move the robot, allowing the map to be updated as the robot traverses the environment:

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The occupancy grid can be observed in RViz2 as the robot moves. When the map is sufficient, save using:

```
ros2 run nav2_map_server map_saver_cli -f my_map
```

#### Using the map with Navigation2

The saved map can be used for localisation going forward. The launch file `map.launch.py` starts the `map_server` from the `nav2_map_server` package. `use_sim_time: True` is set for simulation, with the yaml filename provided for configuration parameters.

When using Nav2 packages, a `nav2_lifecycle_manager` must be started for the relevant packages. In this case, `node_names` are `map_server` and `amcl`, configured to autostart.

#### Recording named spots from RViz2

The `PointRecorder` node subscribes to `/initialpose` and saves named poses to `spot-list.yaml` in the `project_path_planning` config directory. Only the `map_server` is required — no localisation or Nav2 stack is needed.

The node accepts a `spot_name` parameter and records the pose each time the **2D Pose Estimate** tool is used in RViz2. Output is written in ROS 2 parameter file format, allowing the file to be passed directly to `move_to_spot`.

Each spot is recorded by running the node once per label:

```
ros2 run project_mapping point_recorder --ros-args -p spot_name:=point1
ros2 run project_mapping point_recorder --ros-args -p spot_name:=point2
ros2 run project_mapping point_recorder --ros-args -p spot_name:=point3
```

The three required spots for this project are `corner1`, `corner2`, and `pedestrian`. Each recorded pose is appended to `~/ros2_ws/src/project_path_planning/config/spot-list.yaml`, preserving previously recorded spots.

### Project localisation

The AMCL node is used to localise the robot within the environment. The localisation launch file includes `map.launch.py` from `project_mapping` so that the map is published under the topic of the same name.

`nav2_amcl` is launched with a configuration yaml file. A ROS 2 node named `SpotRecorder` is also provided. A service is exposed that allows a pose to be retrieved and saved from the robot at the current position in the environment. Coordinates are saved to a text file with a label, enabling these landmarks to be used for future navigation.

An additional package, **project_localisation_interfaces**, is required, as service messages must be defined in an interfaces package. The service message is defined in `MyServiceMessage.srv` as:

```
# request
string label
---
# response
bool success
string msg
geometry_msgs/PoseWithCovarianceStamped pose
```

The `SpotRecorder` subscribes to `amcl_pose`, retrieves the estimated robot position from the particle filter, and saves the result to the text file.

To launch:

```
ros2 launch project_localisation localisation.launch.py
```

The initial pose must be set manually in RViz. To hardcode it, set `initial_pose` in the AMCL configuration file.

`ros2 service list` can be used to confirm the service is ready. To check the service type:

```
ros2 service type /record_spot
```

To call the service:

```
ros2 service call /record_spot "label: corner1"
```

## Navigation

Start the path planning launch file with:

```
ros2 launch project_path_planning path_planner.launch.py
```

Once the starting pose estimate has been set using RViz2, a goal pose can be set via RViz2. The robot will navigate to the goal.

### Navigating to a named spot

The `move_to_spot` node acts as a Nav2 action client for the `NavigateToPose` action. Target coordinates are read from `spot-list.yaml`, with the desired destination supplied as a runtime parameter — no code changes are required to switch between spots.

The full Nav2 stack must be running before use. After setting the initial pose estimate in RViz2:

```
ros2 run project_path_planning move_to_spot --ros-args --params-file ~/ros2_ws/src/project_path_planning/config/spot-list.yaml -p spot_name:=corner1
```

Substituting `corner1` with `corner2` or `pedestrian` navigates to the other recorded spots. The node terminates automatically upon completion of navigation.

## Troubleshooting

```
ros2 param set /robot_state_publisher use_sim_time true
```

## TODO

- Installation instructions
- Simulator and world setup discussion

# Mapping

The `project_mapping` package provides SLAM-based map creation, map serving, and named spot recording for use with the Nav2 navigation stack.

## SLAM with Cartographer

`cartographer.launch.py` starts the `cartographer_node` from `cartographer_ros` with `use_sim_time: True` for simulation time synchronisation. SLAM configuration is loaded from `cartographer.lua`, which controls parameters such as `trajectory_builder_2D.max_range` for laser scanner range.

A `cartographer_occupancy_grid_node` is also started, consuming the submaps published by the SLAM node and republishing them as a standard ROS 2 `OccupancyGrid`. A publish period of 1.0 seconds is used, as map generation is computationally expensive.

```bash
ros2 launch project_mapping cartographer.launch.py
```

Drive the robot through the environment using teleoperation to build the map:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The occupancy grid can be observed in RViz2 as the robot moves. Save the completed map with:

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

## Serving a Map

`map.launch.py` starts `nav2_map_server` with `use_sim_time: True`, loading the map from the `maps/` directory. A `nav2_lifecycle_manager` manages the `map_server` and `amcl` nodes and is configured to autostart.

```bash
ros2 launch project_mapping map.launch.py
```

## Recording Named Spots

The `point_recorder` node subscribes to `/initialpose` and writes named poses to `spot-list.yaml` in the `project_path_planning` config directory. Only the map server is required — no localisation or full Nav2 stack is needed.

Launch the map server and RViz2, then record each spot by running the node with the target label and using the **2D Pose Estimate** tool in RViz2:

```bash
ros2 run project_mapping point_recorder --ros-args -p spot_name:=spot1
ros2 run project_mapping point_recorder --ros-args -p spot_name:=spot2
ros2 run project_mapping point_recorder --ros-args -p spot_name:=example_landmark
```

Each recorded pose is appended to `~/ros2_ws/src/project_path_planning/config/spot-list.yaml` in ROS 2 parameter file format, ready for direct use with `move_to_spot`.
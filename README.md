# Autonomous TurtleBot3 Navigation

This project implements autonomous TurtleBot3 navigation using ROS 2 Humble and Nav2 in simulation.

## Packages

To achieve autonomous navigation, three packages have been created.

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
- Add second TurtleBot3 to the simulation

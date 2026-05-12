# Autonomous TurtleBot3 Navigation

This project implements autonomous TurtleBot3 navigation using ROS 2 Humble and Nav2 in simulation.

## Packages

To achieve autonomous navigation three packages have been created. 

### Project Mapping

#### Using Cartographer ROS

Project mapping package is used to create and save a map of the environment. The launch file `cartographer.launch.py` launches the nodes from the `cartographer_ros` package. 

Executing the `cartographer_node` with `use_sim_time: True` allows for time synchronisation in simulation. This node is used for SLAM. The configuration parameters are provided via the `cartographer.lua` file.

Additionally, the `cartographer_occupancy_grid_node` is launched and listens to the submaps published by SLAM using them to build a ROS 2 occupancy_grid which it also publishes. We pass the publish period of 1.0 seconds as generating the map is expensive and slow. 

To launch this file and start creating the map using SLAM

```
ros2 launch project_mapping cartographer.launch.py
```

To move the robot via teleoperation which allows for the map to be updated as the robot moves through the environment

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use rviz2 to observe the occupancy grid as you move the robot. When the map looks sufficient, save it using 

```
ros2 run nav2_map_server map_saver_cli -f my_map
```

#### Using the map with Navigation2

Now that we have saved the map we can use it for localization going forward. We will use the launch file `map.launch.py` to start the `map_server` from the `nav2_map_server` package. Again, we set `use_sim_time: True` as we are in simulation, and provide the yaml filename for our configuration parameters. 

When using Nav2 packages, we must start a `nav2_lifecycle_manager` for the packages we are using. In this case, the `node_names` are `map_server` and `amcl`. It is set to autostart. 

### Project localisation

Now we will use the AMCL node to localize the robot within the environment. Our launch file starts the `map.launch.py` launch file from `project_mapping` so that the `map` is published under the topic of the same name. 

We launch `nav2_amcl` with a configuration yaml file. Additionally, we have written a ROS 2 node named `SpotRecorder`. In this node we create a service that allows us to retrieve and save a pose from the robot as it is in the environment. The coordinates will be saved to a text file with a label so that we can use these landmarks for future navigation. 

To achieve this, an additional package **project_localisation_interfaces** is created. This is because the service message must be defined in an interfaces package. Once we define our service message in `MyServiceMessage.srv` as:

```
# request
string label
---
# response
bool success
string msg
geometry_msgs/PoseWithCovarianceStamped pose
```

We can return to the `SpotRecorder` which subscribes to the `amcl_pose`, retrieves the estimated position of the robot achieved via the particle filter, and saves it to our text file.

To launch the file use:

```
ros2 launch project_localisation localisation.launch.py
```

The initial pose must be set manually in RViz. To hardcode it, set initial_pose in the AMCL configuration file.

We can use `ros2 service list` to ensure the service is ready to use. To check the service type use `ros2 service type /record_spot`. To use the service:

```
ros2 service call /record_spot "label: corner1"
```

## Navigation

start the path planning launch file with

```
ros2 launch project_path_planning path_planner.launch.py
```

Once the starting pose estimate has been set using RViz2, set a goal pose using RViz2. The robot will now navigate to the goal. 

## Troubleshooting 

```
ros2 param set /robot_state_publisher use_sim_time true
```

## TODO

- installation
- Simulator, world discussion. 
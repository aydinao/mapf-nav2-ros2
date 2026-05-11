# Mapping

A launch file launches the cartographer_node from the cartographer_ros package. The necessary parameters and configurations are added for the node to perform SLAM.

The trajectory_builder_2D.max_range parameter in cartographer.lua sets the maximum range of the laser scanner that is used for map building.

Launching this will allow us to create a map of the simulated environment by teleoperating the robot.

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

We save the map 

Then launch the map launch file which starts the map server along with the relevant lifecycle manager. The map is provided to map server which makes it available to other nodes.


# Localisation

The `project_localisation` package provides AMCL-based robot localisation and a service for saving named pose coordinates to a file.

## AMCL Localisation

`localisation.launch.py` includes `map.launch.py` from `project_mapping`, ensuring the map is published before AMCL starts. The `nav2_amcl` node is then launched with configuration from `amcl_config.yaml`.

```bash
ros2 launch project_localisation localisation.launch.py
```

AMCL uses a particle filter to estimate the robot's position within the map. By default, an initial pose must be provided via the **2D Pose Estimate** tool in RViz2. To skip this manual step, set `set_initial_pose: true` in `amcl_config.yaml` alongside the known starting coordinates.

Driving the robot through the environment causes the particle cloud to converge on the correct position, indicated by the cloud becoming more tightly grouped.

## Spot Recorder Service

The `spots_to_file` node provides a `/record_spot` service that saves the current AMCL pose estimate to a text file with a user-supplied label. The `project_localisation_interfaces` package is required, as the service message is defined there.

Confirm the service is available:

```bash
ros2 service list
ros2 service type /record_spot
```

Record the robot's current position under a label:

```bash
ros2 service call /record_spot "label: corner1"
```

A success response confirms the pose has been written to the output file.
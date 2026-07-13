# Localisation Interfaces

The `project_localisation_interfaces` package defines the service message used by the spot recorder node in `project_localisation`.

## Service Definition

`MyServiceMessage.srv` defines the `/record_spot` service interface:

```
# request
string label
---
# response
bool success
string msg
geometry_msgs/PoseWithCovarianceStamped pose
```

In ROS 2, service and message definitions must reside in a dedicated interfaces package separate from the nodes that use them. This package is declared as a dependency of `project_localisation`.
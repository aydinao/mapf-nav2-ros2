# Localization

We will use the AMCL node to localize the robot within the environment.

The launch file launches AMCL node and the necessary parameters for configuration.

We include the launch for the map server so that the map from the mapping package is loaded.

We start with global localisation and so we teleoperate the robot around the environment and observe that the particle cloud should get smaller. The grouped particles indicate that the likelihood of the robot being in this area has increased.

We use a localtion table with 3 points in the environment with a tag naming it. We will use these coordinates later.

Instead of manually adding the spots, a service is created that saves these spots into a text file for us. We can simply drive to a spot we want to save the coordinates of and then launch a node named spot_recorder in the file spots_to_file.py. The node contains a service server named /save_spot that takes a string as input. 

We can simply call this service with a string that we want to use as a label, and the coordinate with its label will be written to a file.

We see a message returned to indicate the write was a success.

ros2 service call /record_spot "label: corner1"
from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot3_gazebo'),
                             'launch', 'turtlebot3_world.launch.py')
            )
        ),
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('project_localisation'), 'launch', 'localisation.launch.py'])
        ),
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('project_path_planning'), 'launch', 'path_planner.launch.py'])
        ),
    ])

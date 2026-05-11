from ament_index_python import get_package_share_directory
import os

import launch
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    nav2_yaml = PathJoinSubstitution([FindPackageShare('project_localisation'), 'config', 'amcl_config.yaml'])
    nav2_yaml_ = os.path.join(get_package_share_directory('project_localisation'), 'config', 'amcl_config.yaml')
    return LaunchDescription([
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('project_mapping'), 'launch', 'map.launch.py'])
            
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml_]
        ),
        Node(
            package='project_localisation',
            executable='spots_to_file',
            name='spots_to_file',
            output='screen'
            )
      
    ])
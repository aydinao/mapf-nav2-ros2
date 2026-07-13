import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ROBOTS = ['tb3_0', 'tb3_1']


def generate_launch_description():
    default_map = os.path.join(get_package_share_directory('nav2_bringup'),
                               'maps', 'turtlebot3_world.yaml')
    config_dir = os.path.join(get_package_share_directory('multi_robot'), 'config')

    actions = [
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Full path to the map yaml file to load'
        ),
        # One shared map server; both AMCLs subscribe to /map.
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'yaml_filename': LaunchConfiguration('map')}]
        ),
    ]

    for ns in ROBOTS:
        actions.append(Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            namespace=ns,
            output='screen',
            parameters=[os.path.join(config_dir, f'{ns}_amcl.yaml')]
        ))

    actions.append(Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localisation',
        output='screen',
        parameters=[{'use_sim_time': True},
                    {'autostart': True},
                    {'bond_timeout': 0.0},
                    {'node_names': ['map_server'] + [f'{ns}/amcl' for ns in ROBOTS]}]
    ))

    return LaunchDescription(actions)

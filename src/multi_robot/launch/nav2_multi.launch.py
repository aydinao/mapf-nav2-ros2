import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

ROBOTS = ['tb3_0', 'tb3_1']


def generate_launch_description():
    config_dir = os.path.join(get_package_share_directory('multi_robot'), 'config')
    bt_xml = os.path.join(get_package_share_directory('project_path_planning'),
                          'config', 'bt.xml')

    actions = []
    lifecycle_nodes = []

    for ns in ROBOTS:
        params = os.path.join(config_dir, f'{ns}_nav2_params.yaml')
        actions += [
            Node(
                namespace=ns,
                package='nav2_controller',
                executable='controller_server',
                name='controller_server',
                output='screen',
                parameters=[params]
            ),
            Node(
                namespace=ns,
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                parameters=[params]
            ),
            Node(
                namespace=ns,
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                parameters=[params]
            ),
            Node(
                namespace=ns,
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                parameters=[params,
                            {'default_nav_to_pose_bt_xml': bt_xml}]
            ),
        ]
        lifecycle_nodes += [f'{ns}/controller_server', f'{ns}/planner_server',
                            f'{ns}/behavior_server', f'{ns}/bt_navigator']

    actions.append(Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_planning',
        output='screen',
        parameters=[{'use_sim_time': True},
                    {'autostart': True},
                    {'bond_timeout': 0.0},
                    {'node_names': lifecycle_nodes}]
    ))

    return LaunchDescription(actions)

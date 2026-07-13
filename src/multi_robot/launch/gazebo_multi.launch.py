import os
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ROBOTS = [
    {'name': 'tb3_0', 'x': '-2.0', 'y': '-0.5', 'yaw': '0.0'},
    {'name': 'tb3_1', 'x': '2.0', 'y': '0.5', 'yaw': '3.14159'},
]


def write_namespaced_sdf(model_sdf_path, namespace):
    """Copy the burger SDF with frame names prefixed by the robot namespace.

    Topics are namespaced by spawn_entity's -robot_namespace, but the frame
    names baked into the gazebo plugins (odom, base_footprint, base_scan)
    are not, so they are rewritten here (same approach as the upstream
    turtlebot3_gazebo multi_robot.launch.py).
    """
    tree = ET.parse(model_sdf_path)
    root = tree.getroot()
    for tag in root.iter('odometry_frame'):
        tag.text = f'{namespace}/odom'
    for tag in root.iter('robot_base_frame'):
        tag.text = f'{namespace}/base_footprint'
    for tag in root.iter('frame_name'):
        tag.text = f'{namespace}/base_scan'
    out_path = os.path.join(tempfile.gettempdir(), f'{namespace}_burger.sdf')
    with open(out_path, 'w') as f:
        f.write('<?xml version="1.0" ?>\n' + ET.tostring(root, encoding='unicode'))
    return out_path


def generate_launch_description():
    os.environ.setdefault('TURTLEBOT3_MODEL', 'burger')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    model_sdf = os.path.join(tb3_gazebo, 'models', 'turtlebot3_burger', 'model.sdf')
    urdf_path = os.path.join(tb3_gazebo, 'urdf', 'turtlebot3_burger.urdf')
    world = os.path.join(tb3_gazebo, 'worlds', 'turtlebot3_world.world')

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    gui = LaunchConfiguration('gui')

    actions = [
        DeclareLaunchArgument('gui', default_value='true',
                              description='Start gzclient alongside gzserver'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
            launch_arguments={'world': world}.items()
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
            condition=IfCondition(gui)
        ),
    ]

    for robot in ROBOTS:
        ns = robot['name']
        sdf_path = write_namespaced_sdf(model_sdf, ns)
        actions += [
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                namespace=ns,
                output='screen',
                parameters=[{
                    'use_sim_time': True,
                    'robot_description': robot_description,
                    'frame_prefix': f'{ns}/',
                }],
            ),
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                name=f'spawn_{ns}',
                output='screen',
                arguments=[
                    '-entity', ns,
                    '-file', sdf_path,
                    '-robot_namespace', ns,
                    '-x', robot['x'],
                    '-y', robot['y'],
                    '-z', '0.01',
                    '-Y', robot['yaw'],
                ],
            ),
        ]

    return LaunchDescription(actions)

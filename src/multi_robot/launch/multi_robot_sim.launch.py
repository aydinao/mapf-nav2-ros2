from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true',
                              description='Start gzclient alongside gzserver'),
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('multi_robot'), 'launch', 'gazebo_multi.launch.py']),
            launch_arguments={'gui': LaunchConfiguration('gui')}.items()
        ),
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('multi_robot'), 'launch', 'localisation_multi.launch.py'])
        ),
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('multi_robot'), 'launch', 'nav2_multi.launch.py'])
        ),
    ])

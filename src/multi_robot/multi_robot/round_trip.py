import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(navigator, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def main(args=None):
    rclpy.init(args=args)
    # Run inside a robot namespace with: --ros-args -r __ns:=/tb3_0
    navigator = BasicNavigator(node_name='round_trip')

    navigator.declare_parameter('start_x', -2.0)
    navigator.declare_parameter('start_y', -0.5)
    navigator.declare_parameter('start_yaw', 0.0)
    navigator.declare_parameter('goal_x', 0.55)
    navigator.declare_parameter('goal_y', 0.55)
    navigator.declare_parameter('goal_yaw', 0.0)
    # Publish /initialpose from the start spot before navigating. Leave False
    # when AMCL is configured with set_initial_pose or already localised.
    navigator.declare_parameter('publish_initial_pose', False)

    p = {name: navigator.get_parameter(name).value
         for name in ['start_x', 'start_y', 'start_yaw', 'goal_x', 'goal_y', 'goal_yaw']}
    start = make_pose(navigator, p['start_x'], p['start_y'], p['start_yaw'])
    goal = make_pose(navigator, p['goal_x'], p['goal_y'], p['goal_yaw'])

    # waitUntilNav2Active republishes navigator.initial_pose to /initialpose
    # until an amcl_pose arrives; left unset it is (0,0) — the centre pillar —
    # which delocalises the robot. Seed it with the start spot instead.
    navigator.initial_pose = start
    if navigator.get_parameter('publish_initial_pose').value:
        navigator.setInitialPose(start)

    navigator.waitUntilNav2Active(localizer='amcl')

    for label, target in [('goal', goal), ('start', start)]:
        navigator.get_logger().info(
            f'Navigating to {label}: x={target.pose.position.x:.2f}, y={target.pose.position.y:.2f}')
        navigator.goToPose(target)
        while not navigator.isTaskComplete():
            rclpy.spin_once(navigator, timeout_sec=1.0)

        result = navigator.getResult()
        if result != TaskResult.SUCCEEDED:
            navigator.get_logger().error(f'Failed to reach {label} (result: {result}), aborting round trip')
            rclpy.shutdown()
            return

        navigator.get_logger().info(f'Reached {label}')

    navigator.get_logger().info('Round trip complete!')
    rclpy.shutdown()


if __name__ == '__main__':
    main()

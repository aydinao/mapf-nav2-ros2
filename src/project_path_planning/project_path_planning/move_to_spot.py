import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class MoveToSpot(Node):

    def __init__(self):
        super().__init__('move_to_spot', allow_undeclared_parameters=True,
                         automatically_declare_parameters_from_overrides=True)

        spot_name = self.get_parameter('spot_name').get_parameter_value().string_value
        if not spot_name:
            self.get_logger().error('spot_name parameter is required')
            return

        x = self.get_parameter(f'{spot_name}_x').get_parameter_value().double_value
        y = self.get_parameter(f'{spot_name}_y').get_parameter_value().double_value
        yaw = self.get_parameter(f'{spot_name}_yaw').get_parameter_value().double_value

        self.get_logger().info(
            f'Navigating to "{spot_name}": x={x:.3f}, y={y:.3f}, yaw={yaw:.3f}'
        )

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('Waiting for navigate_to_pose action server...')
        self._action_client.wait_for_server()

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self._send_goal_future = self._action_client.send_goal_async(
            goal, feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by action server')
            rclpy.shutdown()
            return
        self.get_logger().info('Goal accepted — navigating...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        pass

    def result_callback(self, future):
        self.get_logger().info('Navigation complete!')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = MoveToSpot()
    rclpy.spin(node)


if __name__ == '__main__':
    main()

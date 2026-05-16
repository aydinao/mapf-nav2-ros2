import math
import os
import yaml

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped


SPOT_LIST_FILE = os.path.join(
    os.path.expanduser('~'), 'ros2_ws', 'src',
    'project_path_planning', 'config', 'spot-list.yaml'
)


class PointRecorder(Node):
    def __init__(self):
        super().__init__('point_recorder')
        self.declare_parameter('spot_name', 'spot')
        self.spot_name = self.get_parameter('spot_name').get_parameter_value().string_value
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped, '/initialpose', self.subscription_callback, 10
        )
        self.get_logger().info(
            f'PointRecorder ready — label: "{self.spot_name}". '
            'Use 2D Pose Estimate in RViz2 to record.'
        )

    def subscription_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w
        yaw = 2.0 * math.atan2(qz, qw)

        self.get_logger().info(
            f'Recording "{self.spot_name}": x={x:.3f}, y={y:.3f}, yaw={yaw:.3f}'
        )

        if os.path.exists(SPOT_LIST_FILE):
            with open(SPOT_LIST_FILE, 'r') as f:
                cur_yaml = yaml.safe_load(f) or {}
        else:
            os.makedirs(os.path.dirname(SPOT_LIST_FILE), exist_ok=True)
            cur_yaml = {}

        cur_yaml.setdefault('move_to_spot', {}).setdefault('ros__parameters', {})
        params = cur_yaml['move_to_spot']['ros__parameters']
        params[f'{self.spot_name}_x'] = float(x)
        params[f'{self.spot_name}_y'] = float(y)
        params[f'{self.spot_name}_yaw'] = float(yaw)

        with open(SPOT_LIST_FILE, 'w') as f:
            yaml.safe_dump(cur_yaml, f)

        self.get_logger().info(f'Saved to {SPOT_LIST_FILE}')


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = PointRecorder()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

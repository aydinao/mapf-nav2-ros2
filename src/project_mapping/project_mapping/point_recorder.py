from ament_index_python import get_package_share_directory
import os
import yaml

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped


class PointRecorder(Node):
    def __init__(self):
        super().__init__("point_recorder")
        self.subscription = self.create_subscription(PointStamped, '/clicked_point', self.subscription_callback, 10)
        self.yaml_file = os.path.expanduser('/home/user/ros2_ws/src/project_mapping/config/points_on_map.yaml')
    
    def subscription_callback(self, msg):
        self.point_to_record = msg.point
        self.get_logger().info("The published point is %s" %msg.point)
        data = {
                'x': float(msg.point.x),
                'y': float(msg.point.y),
                'z': float(msg.point.z),
            }

        with open(self.yaml_file, 'r') as f:
            cur_yaml = yaml.safe_load(f) or {}

        cur_yaml[f'point_{len(cur_yaml) + 1}'] = data

        with open(self.yaml_file, 'w') as f:
            yaml.safe_dump(cur_yaml, f)


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

from ament_index_python import get_package_share_directory
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped

from project_localisation_interfaces.srv import MyServiceMessage

yaml_file = os.path.join(get_package_share_directory('project_localisation'), 'config', '') 

class SpotRecorder(Node):

    def __init__(self):
        super().__init__('spot_recorder')
        self.srv = self.create_service(MyServiceMessage, '/save_spot', self.save_retrieved_pose)
        self.subscription = self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.subscription_callback, 10)
        self.latest_pose = None
        # self.publisher = self.create_publisher(PoseWithCovarianceStamped, '/retrieve_pose', 1)
        # self.subscriber = self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', 1, self.listener_callback)

    def subscription_callback(self, msg):
        # self.get_logger().info("I heard: %s" %msg)

        self.latest_pose = msg
    
    def save_retrieved_pose(self, request, response):
        if self.latest_pose is None:
            self.get_logger().info("No AMCL pose received yet, pose is: %s" %self.latest_pose)
            response.success = False
            response.msg = "No AMCL pose received yet"
            return response
        self.get_logger().info("The pose is %s" %self.latest_pose)
        response.success = True
        response.pose = self.latest_pose

        location = request.label
        file = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'src', 'project_localisation', 'data', 'spots.txt')
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'a') as text_file:
            text_file.write(location + "\n" + str(self.latest_pose.pose) + "\n")
        self.get_logger().info(f'Label: {request.label}, Pose: {self.latest_pose.pose.pose}')
        self.get_logger().info(f'Writing to: {file}')
        return response
def main(args=None):
    rclpy.init(args=args)

    spot_recorder = SpotRecorder()

    rclpy.spin(spot_recorder)

    rclpy.shutdown()

if __name__ == '__main__':
    main()


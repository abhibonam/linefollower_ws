import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np


class LineFollower(Node):
    def __init__(self):
        super().__init__('line_follower')
        self.bridge = CvBridge()

        # Subscriber to camera
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # Publisher for velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info("Line follower node started, waiting for images...")

    def image_callback(self, msg):
        self.get_logger().info("Received image frame")

        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Crop lower half of the image (focus on road)
        height, width, _ = cv_image.shape
        crop_img = cv_image[int(height/2):height, :]

        # Convert to grayscale + threshold
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        # Calculate centroid
        M = cv2.moments(thresh)
        twist = Twist()

        if M['m00'] > 0:  # Line detected
            cx = int(M['m10'] / M['m00'])
            err = cx - width // 2
            twist.linear.x = 0.1   # Move forward
            twist.angular.z = -float(err) / 200.0  # Adjust steering
            self.get_logger().info(f"Line detected: cx={cx}, err={err}")
        else:  # No line detected
            twist.linear.x = 0.0
            twist.angular.z = 0.3  # Rotate to search
            self.get_logger().warn("No line detected, rotating...")

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = LineFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

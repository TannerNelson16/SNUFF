#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
import numpy as np

class FlameDetectionNode(Node):
    def __init__(self):
        super().__init__('flame_detection_node')
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',  # Replace with your actual image topic
            self.image_callback,
            10)
        self.cv_bridge = CvBridge()

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Detect flames in the image
            flame_detected, result_image = self.detect_flame(cv_image)

            if flame_detected:
                self.get_logger().info('Flame detected!')
            else:
                self.get_logger().info('No flame detected.')

            # Display the result image (optional)
            cv2.imshow('Flame Detection', result_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error('Error processing image: {}'.format(str(e)))

    def detect_flame(self, image):
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define a color range for flames in HSV
        lower_bound = np.array([0, 100, 100], dtype=np.uint8)
        upper_bound = np.array([20, 255, 255], dtype=np.uint8)

        # Create a mask using the color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # Apply the mask to the original image
        result = cv2.bitwise_and(image, image, mask=mask)

        # Convert the result to grayscale
        gray_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        # Threshold the grayscale image
        _, binary_result = cv2.threshold(gray_result, 50, 255, cv2.THRESH_BINARY)

        # Find contours in the binary image
        contours, _ = cv2.findContours(binary_result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check if any contours are found
        if contours:
            # Draw bounding boxes around detected flames
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            return True, image  # Flame detected
        else:
            return False, image  # No flame detected

def main(args=None):
    rclpy.init(args=args)
    node = FlameDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

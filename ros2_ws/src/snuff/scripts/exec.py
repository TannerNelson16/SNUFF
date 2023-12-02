#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
import numpy as np
import rclpy
from std_msgs.msg import String

class FlameDetectionNode(Node):
    def __init__(self):
        super().__init__('flame_detection_node')
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',  # Replace with your actual image topic
            self.image_callback,
            10)
        self.cv_bridge = CvBridge()
        self.init_video_window()
       # rclpy.init()
        self.publisher = self.create_publisher(String, 'flame_info', 10)
    
    def init_video_window(self):
        # Create a window for displaying the video feed
        cv2.namedWindow('Flame Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Flame Detection', 640, 480)
    
    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Display the video feed
            cv2.imshow('Flame Detection', cv_image)
            cv2.waitKey(1)

            # Detect flames in the image
            flame_detected, result_image = self.detect_flame(cv_image)

            if flame_detected:
                self.get_logger().info('Flame detected!')

                # Display the result image with bounding boxes
                cv2.imshow('Flame Detection', result_image)
                cv2.waitKey(1)
            else:
                self.get_logger().info('No flame detected.')

        except Exception as e:
            self.get_logger().error('Error processing image: {}'.format(str(e)))
    def detect_flame(self, image):
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define a color range for flames in HSV
        lower_bound = np.array([0, 0, 255], dtype=np.uint8)
        upper_bound = np.array([179, 50, 255], dtype=np.uint8)

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

        # Create a copy of the input image to modify
        result_image = image.copy()

        # Check if any contours are found
        flame_detected = False
        
        if contours:
            # Draw bounding boxes around detected flames
            for contour in contours:
                # Calculate the bounding box area
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                aspect_ratio = w / float(h) if h != 0 else 0
                circularity = 4 * np.pi * area / (cv2.arcLength(contour, True) ** 2) if cv2.arcLength(contour, True) != 0 else 0
                hull = cv2.convexHull(contour)
                convexity = area / cv2.contourArea(hull) if cv2.contourArea(hull) != 0 else 0
                # Adjust the threshold for the bounding box area
                if area > 100:  # Adjust this threshold based on your scene
                    
                    cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    flame_detected = True
                # Calculate the bounding box area
               # x, y, w, h = cv2.boundingRect(contour)
               # area = cv2.contourArea(contour)
               # center_x = x + w // 2
               # center_y = y + h // 2
                
                # Additional criteria based on shape

                # Adjust these thresholds based on your observations
                #if 0.5 < aspect_ratio < 2.0 and circularity < 0.6 and convexity < 0.8:
                #    cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #    flame_detected = True

                    # Publish flame information
                    flame_msg = String()
                    flame_msg.data = f"Flame detected at x: {x}, y: {y}, width: {w}, height: {h}"
                    self.publisher.publish(flame_msg)
        
        if flame_detected:
            return True,result_image
        else:
            return False,image

    def __del__(self):
        # Close the video window when the script ends
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = FlameDetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

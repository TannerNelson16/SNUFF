#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from apriltag_msgs.msg import AprilTagDetectionArray
from math import sin, cos

class CameraController(Node):
    def __init__(self):
        super().__init__('camera_controller')
        self.turret_pub = self.create_publisher(String, '/turret', 10)
       # self.tilt_pub = self.create_publisher(Float64, '/tilt_cmd', 10)
        self.apriltag_sub = self.create_subscription(
            AprilTagDetectionArray,
            '/detections',
            self.apriltag_callback,
            10
        )

        # Set initial pan and tilt values
        self.pan_value = 0
        self.tilt_value = 0
        self.pan_step = 0.5
        self.tilt_step = 0.5
        # Timer for continuous panning
        self.timer = self.create_timer(0.055, self.continuous_panning)

    def continuous_panning(self):
        
        # Define the maximum and minimum pan angles
        max_pan_angle = 100
        min_pan_angle = -100
        
        # Adjust pan value for continuous panning
        self.pan_value = self.pan_value + self.pan_step

        # Check if the pan value exceeds the maximum or minimum pan angle
        if self.pan_value >= max_pan_angle or self.pan_value <= min_pan_angle:
            # Reverse the panning direction

            self.pan_step = -self.pan_step
        
        # Publish pan command
        self.publish_pan_tilt()
   
    def apriltag_callback(self, msg):
        # Check if any apriltags are detected
        if msg.detections:
            # Assume only one detection for simplicity
            detection = msg.detections[0]

            #'centre' attribute for tag center coordinates
            tag_center_x = detection.centre.x
            tag_center_y = detection.centre.y
            
           # if self.pan_step < 0:
            #    self.pan_step = 0
            #    self.pan_value += -0.1
            #    self.timer = self.create_timer(1.0, self.continuous_tilting)
            #if self.pan_step > 0:
            #    self.pan_step = 0
            #    self.pan_value += 0.1
            #    self.timer = self.create_timer(1.0, self.continuous_tilting)
            #self.timer = self.create_timer(1.0, self.continuous_tilting)
            print(tag_center_y)
            if tag_center_x >= 300 and tag_center_x <= 310:
                self.pan_step = 0
         #       self.pan_value += -0.05
         #       print(tag_center_y)
                self.timer = self.create_timer(0.1, self.continuous_tilting)

           # if tag_center_x <= 55: 
           #     self.pan_step = 0
            #    self.pan_value += 0.05
            #    print(tag_center_y)
            #    self.timer = self.create_timer(1.0, self.continuous_tilting)
            
            if tag_center_y >= 240 and tag_center_y <= 260:
                self.tilt_step = 0 
               # self.tilt_value += 0.05

            self.publish_pan_tilt()

    def continuous_tilting(self):
    
        # Define the maximum and minimum pan angles
        max_tilt_angle = 60
        min_tilt_angle = -60
    
        # Adjust pan value for continuous panning
        self.tilt_value = self.tilt_value + self.tilt_step

        # Check if the pan value exceeds the maximum or minimum pan angle
        if self.tilt_value >= max_tilt_angle or self.tilt_value <= min_tilt_angle:
            # Reverse the panning direction

            self.tilt_step = -self.tilt_step
    
        # Publish pan command
        
        self.publish_pan_tilt()
    

    def publish_pan_tilt(self):
        # Publish pan command
        turret_msg = String()
        turret_msg.data = f"{self.pan_value} {self.tilt_value}"
        self.turret_pub.publish(turret_msg)

        # Publish tilt command
        #tilt_msg = Float64()
        #tilt_msg.data = self.tilt_value
        #self.tilt_pub.publish(tilt_msg)

def main(args=None):
    rclpy.init(args=args)

    camera_controller = CameraController()

    rclpy.spin(camera_controller)

    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


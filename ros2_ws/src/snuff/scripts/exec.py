#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32
from apriltag_msgs.msg import AprilTagDetectionArray
from math import sin, cos, radians

class CameraController(Node):
    def __init__(self):
        super().__init__('camera_controller')
        self.turret_pub = self.create_publisher(String, '/turret', 10)
        self.flame_sub = self.create_subscription(
            String,
            'flame_info',
            self.flame_info_callback,
            10)
        self.get_logger().info('Flame Info Subscriber Node initialized.')
        self.publisher = self.create_publisher(String, '/object_found', 10)
        self.ir_sensor_sub = self.create_subscription(
            Int32,
            'ir_sensor_data',
            self.ir_data_callback,
            10)
        

        # Set initial pan and tilt values
        self.pan_value = 65
        self.tilt_value = 0
        self.tilt_inc = 20
        self.pan_step = -0.05
        self.tilt_step = 0.5
        self.max_pan_angle = 100
        self.min_pan_angle = -100
        self.oscillation_amplitude = 0
        self.oscillation_frequency = 0
        self.flame_found = 0
        self.ir_data = 1
        # Timer for continuous panning
        


    
    def ir_data_callback(self, msg):
        self.ir_data = msg.data
        self.get_logger().info("Received IR data: %d" % self.ir_data)
        if self.ir_data == 0:
            self.timer = self.create_timer(0.05, self.continuous_panning)
            self.timer = self.create_timer(1, self.publish_message)

    def continuous_panning(self):
        
        
        # Adjust pan value for continuous panning
        self.pan_value = self.pan_value + self.pan_step
       
#       self.pan_value += self.oscillation_step * sin(radians(self.pan_value))        
        time = self.get_clock().now().to_msg().sec  # Use time as a basis for oscillation
        oscillation = self.oscillation_amplitude * sin(self.oscillation_frequency * time)
        self.pan_value += oscillation# Check if the pan value exceeds the maximum or minimum pan angle
        if self.pan_value >= self.max_pan_angle or self.pan_value <= self.min_pan_angle:
            # Reverse the panning direction
            
            self.pan_step = -self.pan_step
            
            if self.tilt_value >= 60 or self.tilt_value <=-60:
                self.tilt_inc = -self.tilt_inc

            self.tilt_value = self.tilt_value + self.tilt_inc
       
       # Publish pan command
        self.publish_pan_tilt()
   
#    def apriltag_callback(self, msg):
    def flame_info_callback(self, msg):
        # Check if any apriltags are detected
        #if msg.detections:
            # Assume only one detection for simplicity
            #detection = msg.detections[0]

            #'centre' attribute for tag center coordinates
        #    tag_center_x = detection.centre.x
        #    tag_center_y = detection.centre.y
        flame_data = msg.data.split(', ')
       # print(flame_data)
        if len(flame_data) >= 4:
            # Extract individual values
            tag_center_x = int(flame_data[0].split(': ')[1])
            tag_center_y = int(flame_data[1].split(': ')[1])
            print(tag_center_x)
            print(tag_center_y)
            
            if tag_center_x >= 310 and tag_center_x <= 320:
                self.pan_step = 0
                if tag_center_y > 250:
                    self.tilt_step = -self.tilt_step
                self.timer = self.create_timer(0.1, self.continuous_tilting)

            
            if tag_center_y >= 230 and tag_center_y <= 270:
                self.tilt_step = 0
                self.pan_step = 0
                self.oscillation_amplitude = 0.4
                self.oscillation_frequency = 500000
                self.flame_found = 1
                # Adjust pan value for continuous panning
                self.tilt_inc = 0
            
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
         #   self.timer = self.create_timer(1, self.publish_message)
        # Publish pan command
        
        self.publish_pan_tilt()

    def spray(self):

        #max_spray_angle = self.spray_max
        #min_spray_angle = self.spray_max
        #spray_inc = 0.5
        self.pan_value += self.pan_step
        self.pan_value = self.pan_value + spray_inc

        if self.pan_value >= max_spray_angle or self.pan_value <= min_spray_angle:
            spray_inc = -spray_inc

    def publish_pan_tilt(self):
        # Publish pan command
        turret_msg = String()
        turret_msg.data = f"{self.pan_value} {self.tilt_value}"
        self.turret_pub.publish(turret_msg)

        # Publish tilt command
        #tilt_msg = Float64()
        #tilt_msg.data = self.tilt_value
        #self.tilt_pub.publish(tilt_msg)

    def publish_message(self):
        if self.flame_found > 0:
            msg = String()
            msg.data = 'object_found'
            self.publisher.publish(msg)
            self.get_logger().info('Published: %s' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    camera_controller = CameraController()

    rclpy.spin(camera_controller)

    camera_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


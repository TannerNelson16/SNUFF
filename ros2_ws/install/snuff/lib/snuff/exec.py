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
 #       self.ir_sensor_sub = self.create_subscription(
 #           Int32,
 #           'ir_sensor_data',
 #           self.ir_data_callback,
 #           10)
        

        # Set initial pan and tilt variable values
        self.shutdown_timer = None
        self.pan_value = 99
        self.tilt_value = 0
        self.tilt_inc = 20
        self.pan_step = -0.5
        self.tilt_step = -0.5
        self.max_pan_angle = 100
        self.min_pan_angle = -100
        self.oscillation_amplitude = 0
        self.oscillation_frequency = 0
        self.flame_found = 0
        self.ir_data = 1
      
        # Start continuous panning
        self.timer = self.create_timer(0.1, self.continuous_panning)
        # Start continuous publishing of 
        self.timer = self.create_timer(1, self.publish_message)

    
#    def ir_data_callback(self, msg):
#        self.ir_data = msg.data
#        self.get_logger().info("Received IR data: %d" % self.ir_data)
#        if self.ir_data == 0:
#            self.timer = self.create_timer(0.05, self.continuous_panning)
#            self.timer = self.create_timer(1, self.publish_message)

    def continuous_panning(self):
        
        
        # Adjust pan value for continuous panning
        self.pan_value = self.pan_value + self.pan_step
       
        # Use time as a basis for oscillation
        time = self.get_clock().now().to_msg().sec  
        #Sine wave oscillation
        oscillation = self.oscillation_amplitude * sin(self.oscillation_frequency * time)
        #Adjust Pan by oscillation increment (0 if flame not found yet)
        self.pan_value += oscillation

        if self.pan_value >= self.max_pan_angle or self.pan_value <= self.min_pan_angle:
            # Reverse the panning direction when max_pan angle reached
            
            self.pan_step = -self.pan_step
            
            #increment tilt by 20 to max and min values to get full scan
            if self.tilt_value >= 60 or self.tilt_value <=-60:
                self.tilt_inc = -self.tilt_inc

            self.tilt_value = self.tilt_value + self.tilt_inc
       
       # Publish pan command
        self.publish_pan_tilt()
   
    def flame_info_callback(self, msg):
        
        flame_data = msg.data.split(', ')
        
        #When the flame has been found from opencv, the message will populate here
        if len(flame_data) >= 4:
     
            # Extract individual values
            tag_center_x = int(flame_data[0].split(': ')[1])
            tag_center_y = int(flame_data[1].split(': ')[1])
            
            # Center of frame on x-axis is near 300
            if tag_center_x >= 310 and tag_center_x <= 320:
                #Stop panning motion when flame is in center
                self.pan_step = 0
                if tag_center_y > 310:
                    self.tilt_step = -self.tilt_step
                #Begin continuous tilting
                self.timer = self.create_timer(0.1, self.continuous_tilting)

            # Center of frame on y-axis is near 250
            if tag_center_y >= 250 and tag_center_y <= 300:
                
                #Stop tilting motion when flame is in center
                self.tilt_step = 0
                #Ensure no panning motion
                self.pan_step = 0
                
                #Start oscillation (Spraying Motion)
                self.oscillation_amplitude = 0.4
                self.oscillation_frequency = 500000
                
                #Turn on water jet
                self.flame_found = 1
                
                #Ensure no tilt motion
                self.tilt_inc = 0
                
                #Shutdown node after 8 seconds 
                if not self.shutdown_timer:
                    self.shutdown_timer = self.create_timer(8.0, self.shutdown_callback)


            self.publish_pan_tilt()

    def continuous_tilting(self):
    
        # Define the maximum and minimum pan angles
        max_tilt_angle = 60
        min_tilt_angle = -60
       
        # Adjust pan value for continuous panning
        self.tilt_value = self.tilt_value + self.tilt_step

        # Check if the pan value exceeds the maximum or minimum pan angle
        if self.tilt_value >= max_tilt_angle or self.tilt_value <= min_tilt_angle:
            
            # Reverse the panning direction if needed
            self.tilt_step = -self.tilt_step
        
        # Publish pan command
        self.publish_pan_tilt()

    def publish_pan_tilt(self):
       
       # Publish pan command
        turret_msg = String()
        turret_msg.data = f"{self.pan_value} {self.tilt_value}"
        self.turret_pub.publish(turret_msg)

    def publish_message(self):
        
        #publish message for the water jet to start
        if self.flame_found > 0:
            msg = String()
            msg.data = 'object_found'
            self.publisher.publish(msg)
            self.get_logger().info('Published: %s' % msg.data)

    def shutdown_callback(self):
        #Exit node to shutdown program
        self.get_logger().info("Shutting down the node...")
        self.destroy_node()

def main(args=None):
    #Initiate loop to restart fire detection after extinguising"
    while True:
        rclpy.init(args=args)

        try:
            camera_controller = CameraController()
            rclpy.spin(camera_controller)
        except Exception as e:
            print(f"An error occured: {e}")
        finally:
            camera_controller.destroy_node()
            rclpy.shutdown()
    print("Restarting the script in 5 seconds...")
    timer.sleep(5)

if __name__ == '__main__':
    main()


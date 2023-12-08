#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess

class ESP32Trigger(Node):
    def __init__(self, usb_port='/dev/ttyUSB0', baud_rate=115200):
        super().__init__('esp32_trigger')
        self.subscription = self.create_subscription(
            String,
            'object_found',
            self.object_found_callback,
            10)
        self.usb_port = usb_port
        #self.baud_rate = baud_rate
        #self.serial_connection = None

    def object_found_callback(self, msg):
        if msg.data == 'object_found':
            self.get_logger().info('Received object found message: %s' % msg.data)
            self.trigger_micro_python_script()

    def trigger_micro_python_script(self):
        try:
            # Run the ampy command to execute the MicroPython script on the ESP32
            command = f'ampy --port {self.usb_port} run valve.py'
            subprocess.run(command, shell=True, check=True)
            
            self.get_logger().info('MicroPython script executed on ESP32')

        except subprocess.CalledProcessError as e:
            self.get_logger().error(f'Error executing MicroPython script: {e}')

def main(args=None):
    rclpy.init(args=args)
    esp32_trigger = ESP32Trigger()
    try:
        rclpy.spin(esp32_trigger)
    except KeyboardInterrupt:
        pass
    finally:
        esp32_trigger.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

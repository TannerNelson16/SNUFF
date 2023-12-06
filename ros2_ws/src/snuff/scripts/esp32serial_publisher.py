#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import std_msgs.msg

class ESP32Interface(Node):
    def __init__(self):
        super().__init__('esp32_interface')
        self.publisher_ = self.create_publisher(std_msgs.msg.String, 'ir_sensor_data', 10)
        self.serial_port = serial.Serial('/dev/ttyUSB1', 115200)  # Change this to your ESP32 serial port

        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        if self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode('utf-8').strip()
            msg = std_msgs.msg.String()
            msg.data = data
            print(msg)
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)

    esp32_interface = ESP32Interface()

    try:
        rclpy.spin(esp32_interface)
    except KeyboardInterrupt:
        pass

    esp32_interface.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

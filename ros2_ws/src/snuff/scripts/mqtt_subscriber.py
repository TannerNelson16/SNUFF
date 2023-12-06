#!/usr/bin/env python3
import rclpy
from std_msgs.msg import String
import paho.mqtt.client as mqtt

class MyMqttSubscriber:
    def __init__(self, mqtt_broker, mqtt_port, mqtt_topic, mqtt_username, mqtt_password):
        self.node = rclpy.create_node('mqtt_subscriber_node')
        self.subscription = self.node.create_subscription(
            String,
            'ir_sensor_data',
            self.callback,
            10
        )

        # Initialize MQTT client with authentication
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to MQTT broker
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port

        self.node.get_logger().info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 120)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker successfully!")
            self.mqtt_client.subscribe(self.mqtt_topic)
        else:
            print(f"Failed to connect to MQTT broker with result code {rc}")

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode('utf-8')
        print(f"Received message on topic {msg.topic}: {data}")
        self.node.get_logger().info(f"Received IR sensor data: {data}")

    def callback(self, msg):
        # This is the callback for the ROS 2 subscription
        pass

def main(args=None):
    rclpy.init(args=args)
    mqtt_broker = "38.70.247.173"
    mqtt_port = 1883
    mqtt_topic = "tele/ir_sensor_data/STATE"
    mqtt_username = "Tanner23456"
    mqtt_password = "Tn7281994!"

    my_subscriber = MyMqttSubscriber(mqtt_broker, mqtt_port, mqtt_topic, mqtt_username, mqtt_password)

    try:
        while rclpy.ok():
            rclpy.spin_once(my_subscriber.node, timeout_sec=0.1)
    except KeyboardInterrupt:
        print("Stopping the program.")
    finally:
        my_subscriber.mqtt_client.disconnect()
        print("Disconnected from MQTT")
        my_subscriber.node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


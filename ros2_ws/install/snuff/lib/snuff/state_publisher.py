#!/usr/bin/env python3
import dyn_lib
import time
import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ArmController(Node):

    def __init__(self):
        super().__init__('turret_controller')
        com="/dev/ttyUSB1"
        try:
            self.d=dyn_lib.Dynamixel(DEVICENAME=com, num_joints=2)
            self.d.enable_torque()
        except Exception as e:
            print("Loading of Dynamixel library for servo motors on dev {:s} failed".format(com))
            print(e)
            quit()
        self.subscription = self.create_subscription(
            String,
            'turret',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def move_one(self,joint,angle):
        if joint==5:
            self.d.move_one(int(joint), int(angle))
        else:
            self.d.move_one(int(joint), self.degToCnt(float(angle)))
    
        
    def listener_callback(self, msg):
        p=msg.data
        try:
            if p=="r":  # read joint positions and print
                print(self.d.read())
            elif p[0]=="b":  # read joint positions and print
                v=p.split()
                if len(v)==1:
                    self.d.reboot()
                else:
                    self.d.reboot(int(v[1]))
            elif p=="e":  # enble the motors
                self.d.enable_torque()
            elif p=="d":  # disable the motors
                self.d.disable_torque()
            elif p[0]=="o": # move one joint, "o <joint> <angle>"
                v=p.split()
                self.d.move_one(int(v[1]), self.degToCnt(float(v[2])))
            else: # move both joints "<azimuth> <elevation>"
                v=p.split()
                idx=1
                for value in v:
                    self.move_one(idx, value)
                    idx=idx+1
        except Exception as e:
            print(e)

    def shutdown(self):
        self.d.disable_torque()
        self.d.close()
    def degToCnt(self,deg):
        return int(deg/360*4096+2048)

def main(args=None):
    rclpy.init(args=args)
    arm_controller = ArmController()
    rclpy.spin(arm_controller)
    arm_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

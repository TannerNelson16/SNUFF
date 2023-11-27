#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import sys, tty, termios

#fd = sys.stdin.fileno()
#old_settings = termios.tcgetattr(fd)

from dynamixel_sdk import * # Uses Dynamixel SDK library

class Dynamixel:
    def __init__(self, DEVICENAME='/dev/ttyUSB0', BAUDRATE=1000000, num_joints=5):
        """ Connect to a Dynamixel controller """
        self.num_joints = num_joints 
        #********* DYNAMIXEL Model definition *********
        #***** (Use only one definition at a time) *****
        self.MY_DXL = 'X_SERIES'       # X330 (5.0 V recommended), X430, X540, 2X430
        # MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.
        # MY_DXL = 'PRO_SERIES'   # H54, H42, M54, M42, L54, L42
        # MY_DXL = 'PRO_A_SERIES' # PRO series with (A) firmware update.
        # MY_DXL = 'P_SERIES'     # PH54, PH42, PM54
        # MY_DXL = 'XL320'        # [WARNING] Operating Voltage : 7.4V


        # Control table address
        if self.MY_DXL == 'X_SERIES' or self.MY_DXL == 'MX_SERIES':
            self.ADDR_TORQUE_ENABLE          = 64
            self.ADDR_GOAL_POSITION          = 116
            self.ADDR_PRESENT_POSITION       = 132
            self.DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
            self.DXL_MAXIMUM_POSITION_VALUE  = 4095      # Refer to the Maximum Position Limit of product eManual
            # BAUDRATE                    = 1000000
        elif self.MY_DXL == 'PRO_SERIES':
            self.ADDR_TORQUE_ENABLE          = 562       # Control table address is different in DYNAMIXEL model
            self.ADDR_GOAL_POSITION          = 596
            self.ADDR_PRESENT_POSITION       = 611
            self.DXL_MINIMUM_POSITION_VALUE  = -150000   # Refer to the Minimum Position Limit of product eManual
            self.DXL_MAXIMUM_POSITION_VALUE  = 150000    # Refer to the Maximum Position Limit of product eManual
            #BAUDRATE                    = 57600
        elif self.MY_DXL == 'P_SERIES' or MY_DXL == 'PRO_A_SERIES':
            self.ADDR_TORQUE_ENABLE          = 512        # Control table address is different in DYNAMIXEL model
            self.ADDR_GOAL_POSITION          = 564
            self.ADDR_PRESENT_POSITION       = 580
            self.DXL_MINIMUM_POSITION_VALUE  = -150000   # Refer to the Minimum Position Limit of product eManual
            self.DXL_MAXIMUM_POSITION_VALUE  = 150000    # Refer to the Maximum Position Limit of product eManual
            #BAUDRATE                    = 57600
        elif self.MY_DXL == 'XL320':
            self.ADDR_TORQUE_ENABLE          = 24
            self.ADDR_GOAL_POSITION          = 30
            self.ADDR_PRESENT_POSITION       = 37
            self.DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the CW Angle Limit of product eManual
            self.DXL_MAXIMUM_POSITION_VALUE  = 1023      # Refer to the CCW Angle Limit of product eManual
            #BAUDRATE                    = 1000000   # Default Baudrate of XL-320 is 1Mbps

        # DYNAMIXEL Protocol Version (1.0 / 2.0)
        # https://emanual.robotis.com/docs/en/dxl/protocol2/
        PROTOCOL_VERSION            = 2.0

        # Use the actual port assigned to the U2D2.
        # ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
        #DEVICENAME                  = '/dev/ttyUSB0'

        self.TORQUE_ENABLE               = 1     # Value for enabling the torque
        self.TORQUE_DISABLE              = 0     # Value for disabling the torque
        self.DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold

        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(DEVICENAME)

        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)

        # Open port
        if not self.portHandler.openPort():
            raise Exception("Failed to open port {:s}".format(BAUDRATE))

        # Set port baudrate
        if not self.portHandler.setBaudRate(BAUDRATE):
            raise Exception("Failed to set baudrate to {:d} baud".format(BAUDRATE))

    def reboot(self, joint=None):
        """ reboot joints that are in error states. 
            If joint is specified then reboot that joint.
            If no joint is specified then reboot all of them.
        """
        # reset Dynamixel
        if joint != None:
            dxl_comm_result, dxl_error = self.packetHandler.reboot(self.portHandler, joint)
            return
        for i in range(self.num_joints):
            dxl_comm_result, dxl_error = self.packetHandler.reboot(self.portHandler, i+1)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception("Failed to enable torque: {:s}".format(
                    self.packetHandler.getTxRxResult(dxl_comm_result)))
            elif dxl_error != 0:
                raise Exception("Failed to enable torque: {:s}".format(
                    self.packetHandler.getRxPacketError(dxl_error)))

    def enable_torque(self):
        # Enable Dynamixel Torque
        for i in range(self.num_joints):
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i+1, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception("Failed to enable torque: {:s}".format(self.packetHandler.getTxRxResult(dxl_comm_result)))
            elif dxl_error != 0:
                raise Exception("Failed to enable torque: {:s}".format(self.packetHandler.getRxPacketError(dxl_error)))

    def move(self, joint_positions):
        if len(joint_positions) != self.num_joints:
            raise Exception("Incorrect number of joint positions.  Need {:d} got {:d}".format(self.num_joints,len(joint_positions)))
        for i in range(self.num_joints):
            if (self.MY_DXL == 'XL320'): # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
                dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, i+1, self.ADDR_GOAL_POSITION, joint_positions[i])
            else:
                dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, i+1, self.ADDR_GOAL_POSITION, joint_positions[i])
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception("Failed to send postion: {:s}".format(self.packetHandler.getTxRxResult(dxl_comm_result)))
            elif dxl_error != 0:
                raise Exception("Failed to send postion: {:s}".format(self.packetHandler.getRxPacketError(dxl_error)))

    def move_one(self, joint_number, position):
        if joint_number >  self.num_joints or joint_number<=0:
            raise Exception("Ivalid joint number.  Max = {:d} got {:d}".format(self.num_joints,joint_number))
        if (self.MY_DXL == 'XL320'): # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, joint_number, self.ADDR_GOAL_POSITION, position)
        else:
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, joint_number, self.ADDR_GOAL_POSITION, position)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("Failed to send postion: {:s}".format(self.packetHandler.getTxRxResult(dxl_comm_result)))
        elif dxl_error != 0:
            raise Exception("Failed to send postion: {:s}".format(self.packetHandler.getRxPacketError(dxl_error)))

    def read(self):
        pos=[None]*self.num_joints
        for i in range(self.num_joints):
            # Read present position
            if (self.MY_DXL == 'XL320'): # XL320 uses 2 byte Position Data, Check the size of data in your DYNAMIXEL's control table
                pos[i], dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, i+1, self.ADDR_PRESENT_POSITION)
            else:
                pos[i], dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, i+1, self.ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception("Failed to read postions: {:s}".format(self.packetHandler.getTxRxResult(dxl_comm_result)))
            elif dxl_error != 0:
                raise Exception("Failed to read postions: {:s}".format(self.packetHandler.getRxPacketError(dxl_error)))
        return pos

    def disable_torque(self):
        # Disable Dynamixel Torque
        for i in range(self.num_joints):
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, i+1, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
            if dxl_comm_result != COMM_SUCCESS:
                raise Exception("Failed to disable torque: {:s}".format(self.packetHandler.getTxRxResult(dxl_comm_result)))
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                raise Exception("Failed to disable torque: {:s}".format(self.packetHandler.getRxPacketError(dxl_error)))
                
    def close(self):
        # Close port
        self.portHandler.closePort()

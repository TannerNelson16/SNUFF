import machine
import time

# Define GPIO pins
enable_pin = 25  
in1_pin = 26     
in2_pin = 27     

# Initialize GPIO pins
enable = machine.Pin(enable_pin, machine.Pin.OUT)
in1 = machine.Pin(in1_pin, machine.Pin.OUT)
in2 = machine.Pin(in2_pin, machine.Pin.OUT)

# Function to send a positive pulse to open the valve
def open_valve():
    enable.value(1)
    in1.value(1)
    in2.value(0)
    time.sleep(3)  
    enable.value(0)

# Function to send a negative pulse to close the valve
def close_valve():
    enable.value(1)
    in1.value(0) 
    in2.value(1)
    time.sleep(3) 
    enable.value(0)

open_valve()
print("Valve Open")
time.sleep(3)  
close_valve()
print("Valve Closed")
time.sleep(5)  

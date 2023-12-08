import machine
import time

# Define GPIO pins
in1_pin = 26    
in2_pin = 27    

# Initialize GPIO pins
in1 = machine.Pin(in1_pin, machine.Pin.OUT)
in2 = machine.Pin(in2_pin, machine.Pin.OUT)

# Function to send a positive pulse to open the valve
def open_valve():
    in1.value(1)
    in2.value(0)
    time.sleep(1)
    in1.value(0)
    in2.value(0)

# Function to send a negative pulse to close the valve
def close_valve():
    in1.value(0)
    in2.value(1)
    time.sleep(1)
    in1.value(0)
    in2.value(0)


open_valve()
print("Valve Open")
time.sleep(10) 
close_valve()
print("Valve Closed")


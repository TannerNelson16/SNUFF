import machine
import time

# Define the pin to which the IR sensor is connected
ir_sensor_pin = 15  # Change this to the appropriate GPIO pin

# Setup the IR sensor pin as an input
ir_sensor = machine.Pin(ir_sensor_pin, machine.Pin.IN)

# Setup the USB serial connection
uart = machine.UART(0, baudrate=115200)  # UART0 connected to USB

while True:
    try:
        # Read the state of the IR sensor
        ir_sensor_state = ir_sensor.value()

        # Send the sensor state through USB serial
        uart.write(ir_sensor.value())

        # Wait for a short duration before reading the sensor again
        time.sleep(0.1)

    except Exception as e:
        print("Exception: {}".format(e))
        time.sleep(1)

import time
import os
import pigpio

# Define GPIO pins
TRIGGER_PIN = 4  # Adjust based on wiring
ECHO_PIN = 17     # Adjust based on wiring

# Create pigpio instance
pi = pigpio.pi()

if not pi.connected:
    print("Failed to connect to pigpio daemon!")
    exit()

# Set GPIO modes
pi.set_mode(TRIGGER_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)

# Global variables for timing
pulse_start = None
pulse_end = None

def echo_callback(gpio, level, tick):
    """ Callback function to record the echo signal duration. """
    global pulse_start, pulse_end

    if level == 1:  # Rising edge (echo starts)
        pulse_start = tick
    elif level == 0:  # Falling edge (echo ends)
        pulse_end = tick

# Attach callback to ECHO pin
cb = pi.callback(ECHO_PIN, pigpio.EITHER_EDGE, echo_callback)

def get_distance():
    """Measures the distance using the HC-SR04 sensor with pigpio daemon."""
    global pulse_start, pulse_end

    # Send a 10us pulse to the trigger pin
    pi.write(TRIGGER_PIN, 1)
    time.sleep(0.00001)
    pi.write(TRIGGER_PIN, 0)

    # Wait for a valid measurement
    timeout = time.time() + 1  # 1-second timeout
    while pulse_start is None or pulse_end is None:
        if time.time() > timeout:
            return None  # Timeout, no valid measurement

    # Convert tick counts (in microseconds) to seconds
    elapsed_time = (pulse_end - pulse_start) / 1_000_000.0
#    print(elapsed_time)

    # Calculate distance (Speed of sound = 34300 cm/s)
    distance = (elapsed_time * 34300) / 2

    # Reset timing variables
    pulse_start, pulse_end = None, None

    return round(distance, 2)

def measure(count):
    i = 0
    tally = 0.0
    while i<count:
        tmp = get_distance()
        if tmp != None:
            tally += tmp
            i += 1
            time.sleep(0.5)
        else: continue
    result = (tally / count) / 2.54
    return(result)


current_sample = 0
MAX_SAMPLE = 10
REF_DIST = measure(10)
print("Reference Height: ", '{0:.2f}'.format(REF_DIST))
hist = [0.0] * MAX_SAMPLE
try:
    while True:
        hist[current_sample % MAX_SAMPLE] = ((REF_DIST - measure(5) + .12) * 4 // 1) / 4  # round to 1/4 inch
#        os.system('clear')
        i = 0
        tally = 0
        while i < MAX_SAMPLE:
            print ('{0:.2f}'.format(hist[(current_sample - i) % MAX_SAMPLE]), end=" ")
            tally += hist[(current_sample - i) % MAX_SAMPLE]
            i += 1
        print(":  ", '{0:.2f}'.format(tally / MAX_SAMPLE))
        current_sample += 1
        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    cb.cancel()  # Cancel the callback
    pi.stop()  # Stop pigpio daemon usage




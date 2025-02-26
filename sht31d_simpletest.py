import os
import time
import board
import busio
import adafruit_sht31d
from datetime import datetime

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

outfile = open('sensortmp/data', 'w')

loopcount = 0

temperature1, humidity1 = sensor._read()
temperature4 = temperature3 = temperature2 = temperature1 + .05

while True:
    n = datetime.now()
    temperature4 = temperature3
    temperature3 = temperature2
    temperature2 = temperature1
    time.sleep(10-n.second%10-n.microsecond/1000000.0)
    temperature1, humidity = sensor._read()
    temperature1 = temperature1 + .035
    temperature = (temperature1 + .75*temperature2 + .5*temperature3 + .25*temperature4)/2.5 - (.25/1.8)
    dewpoint = (humidity/100)**.125 *(112+.9*temperature)+.1*temperature-112
    dewpoint = 1.8*dewpoint + 32.0
    temperature = 1.8*temperature + 32.0
    print('{0:.2f}, {1:.2f}, {2:.2f}, {3}'.format(temperature, humidity, dewpoint, datetime.now().isoformat(timespec='seconds')), file=outfile)
    loopcount += 1
    if (loopcount%1 == 0): outfile.flush()
    if (loopcount%360 == 1): os.system("cp sensortmp/data journal.csv")

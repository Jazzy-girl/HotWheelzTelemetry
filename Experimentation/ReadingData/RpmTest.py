"""
Test file for accessing and interpreting the speed of the vehicle.

Input will be a constant series of Pulses from either
    A. Motor Controller through CANbus
    B. From the BMS

There are 48 pulses per revolution.

Speed (m/s) = ( (Rev per min) / 60) * (pi * wheel diameter (m))

"""
import math

PULSES_PER_REV = 48
WHEEL_DIAMETER = 1

pulseData = (None, None) # assume pulseData is (<pulses>, <seconds>)

revolutions = pulseData[0] / 48
rps = revolutions / pulseData[1]

speed_mps = (rps) * (math.pi * WHEEL_DIAMETER)
speed_mph = speed_mps * 2.23694
#!/usr/bin/env python3
import json
import serial.tools.list_ports
import serial
import time

def dump_port_info(port):
    print(dir(port))
    attrs = ['apply_usb_info', 'description', 'device', 'hwid', 'interface',
             'location', 'manufacturer', 'name', 'pid', 'product',
             'serial_number', 'usb_description', 'usb_info', 'vid']
    for attr in attrs:
        if hasattr(port, attr):
            if attr in ["usb_info","usb_description"]:
                print("{attr} : {val}".format(attr=attr, val=getattr(port, attr)()))
            else:
                print("{attr} : {val}".format(attr=attr, val=getattr(port, attr)))
            pass
        pass
    pass

def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # dump_port_info(p)
        if getattr(p, "product", None) and "servotor32" in p.product.lower():
            return p.device
        pass
    pass

sercmd = lambda x: "{}\n".format(x).encode("utf-8")

def move(number, angle_degrees):
    position = 1500
    if abs(angle_degrees) > 90:
        angle_degrees = 90 * angle_degrees / abs(angle_degrees)
    position = 1500.0 + float(angle_degrees) * 1000.0/90.0
    return sercmd("#{}P{}".format(number, position))

def limp(number):
    return sercmd("#{}L".format(number))

KILL = sercmd("K")
CENTER = sercmd("C")
# Need to add read capability before the next two will work.
# VERSION = sercmd("V")
# DEBUG = sercmd("D")

# Head is servo #31
# positive angle = looking left

legs = {
    # Numbers are hip, thigh, knee, in that order.
    "LF":(7,6,5),
    "LM":(11,10,9),
    "LR":(15,14,13),
    "RF":(24,25,26),
    "RM":(20,21,22),
    "RR":(16,17,18),
}

signs = {
    # positive 1 indicates that a positive angle will move the appendage forwards or upwards
    # negative 1 indicates that a positive angle will move the appendage backwards or downwards
    # (so, we'll multiple those guys by -1 to get them in line with the standard)
    "LF":(-1,-1,1),
    "LM":(-1,-1,1),
    "LR":(-1,-1,1),
    "RF":(1,-1,1),
    "RM":(1,-1,1),
    "RR":(1,-1,1),
}

offsets = {
    "LF":(0,0,0),
    "LM":(0,0,0),
    "LR":(0,0,0),
    "RF":(0,0,0),
    "RM":(0,0,0),
    "RR":(0,0,0),
}

with serial.Serial(find_port(), 9600) as ser:
    for leg in legs:
        for i in range(3):
            ser.write(move(legs[leg][i], 20))
    time.sleep(.2)
    for leg in legs:
        for i in range(3):
            ser.write(move(legs[leg][i], -20))
    time.sleep(.2)
    for leg in legs:
        for i in range(3):
            ser.write(move(legs[leg][i], 20))
    time.sleep(.2)
    ser.write(KILL)

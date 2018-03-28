#!/usr/bin/env python3
from functools import update_wrapper
import json
import serial.tools.list_ports
import serial
import time

from hexy import inki

VERBOSE=False

def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)
        pass
    pass

class MockSerial(object):
    def __init__(self):
        vprint("Creating mock serial object.")
        self.is_open = False
        pass

    def open(self):
        vprint("Opening mock serial connection.")
        self.is_open = True

    def close(self):
        vprint("Closing mock serial connection.")
        self.is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def write(self, s):
        if not self.is_open:
            raise RuntimeError("MockSerial not connected!")
        vprint("Command sent to mock serial: {}".format(json.dumps(s.decode("utf-8"))))

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

def find_port(attr="product", value="servotor32", fallback_to_mock=False):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # dump_port_info(p)
        if getattr(p, attr, None) and value.lower() in getattr(p, attr, "").lower():
            return p.device
        pass
    if fallback_to_mock:
        return MockSerial()
    pass

sercmd = lambda x: "{}\n".format(x).encode("utf-8")

def move_cmd(number, angle_degrees, offset=0, sign=1):
    angle_degrees *= sign
    angle_degrees += offset
    position = 1500
    if abs(angle_degrees) > 90:
        angle_degrees = 90 * angle_degrees / abs(angle_degrees)
    position = int(1500.0 + float(angle_degrees) * 1000.0/90.0)
    return sercmd("#{}P{}".format(number, position))

def limp_cmd(number):
    return sercmd("#{}L".format(number))

KILL = sercmd("K")
CENTER = sercmd("C")
# Need to add read capability before the next two will work.
# VERSION = sercmd("V")
# DEBUG = sercmd("D")


def needs_hexy(function):
    def newfunc(_self, *args, **kwargs):
        if not _self.connected():
            raise RuntimeError("Must connect to a hexy before moving!")
        return function(_self, *args, **kwargs)
    update_wrapper(newfunc, function)
    return newfunc

class Hexy(object):
    leg_servos = {
        # Numbers are hip, thigh, knee, in that order.
        "LF":(7,6,5),
        "LM":(11,10,9),
        "LR":(15,14,13),
        "RF":(24,25,26),
        "RM":(20,21,22),
        "RR":(16,17,18),
    }

    servo_signs = {
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

    servo_offsets = {
        "LF":(0,0,0),
        "LM":(0,0,0),
        "LR":(0,0,0),
        "RF":(0,0,0),
        "RM":(0,0,0),
        "RR":(0,0,0),
    }

    default_offsets = {}

    leg_segment_lengths = inki.LEG_LENGTHS

    head_servo = 31
    head_offset = 0
    head_sign = -1 # A positive angle is by default looking left, which I find counterintuitive, so switch that around.

    def __init__(self):
        self.serial = None
        self.legs = []
        self.leg_map = {}
        self.all_servos = []
        for leg in ["LF","LM","LR","RF","RM","RR"]:
            new_leg = Leg(self, servos=self.leg_servos[leg], offsets=self.servo_offsets[leg], signs=self.servo_signs[leg], lengths=self.leg_segment_lengths, origin=(0,0,0))
            setattr(self, leg, new_leg)
            self.legs.append(new_leg)
            self.leg_map[leg] = new_leg
            self.all_servos.extend(new_leg.servos)
        self.head = Head(self, offset=self.head_offset)
        self.all_servos.append(self.head.servo)

    def load_default_offsets_from_file(self, fname):
        with open(fname) as f:
            self.load_default_offsets(json.load(f))

    def load_default_offsets(self, offsets):
        for servo in self.all_servos:
            servo.offset = offsets.get(str(servo.number), servo.offset)

    def connect(self):
        if not self.serial:
            self.serial = find_port(fallback_to_mock=True)
        if not self.serial:
            raise RuntimeError("Unable to find usable serial device!")
        if not self.serial.is_open:
            self.serial.open()

    def disconnect(self):
        if self.serial:
            if self.serial.is_open:
                self.serial.close()

    def reconnect(self):
        self.disconnect()
        self.connect()

    def reset_connection(self):
        self.disconnect()
        self.serial = None
        self.connect()

    def connected(self):
        return self.serial and self.serial.is_open

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    @needs_hexy
    def _move(self, number, position):
        self.serial.write(move_cmd(number, position))

    @needs_hexy
    def _act(self, action):
        self.serial.write(action)

    @needs_hexy
    def _stop(self, number):
        self.serial.write(limp_cmd(number))

    def _sleep(self, milliseconds):
        if isinstance(self.serial, MockSerial):
            vprint("Mock sleeping for {} milliseconds...".format(milliseconds))
        else:
            time.sleep(float(milliseconds)/1000.0)

    @needs_hexy
    def center(self):
        self.serial.write(CENTER)

    @needs_hexy
    def stop(self):
        self.serial.write(KILL)

    @needs_hexy
    def goto_last_position(self):
        for servo in self.legs+[self.head]:
            servo.goto_last_position()
            self._sleep(50)

class Servo(object):
    def __init__(self, hexy, number, offset=0, sign=1, start_angle=None):
        self.hexy = hexy
        self.number = number
        self.offset = offset
        self.sign = sign
        # If I switch over to using servos that tell me their position,
        # I can use that in some cases that currently use last_location
        self.last_location = start_angle

    def set_abs_position(self, degrees):
        movement = move_cmd(self.number, angle_degrees=degrees, offset=self.offset, sign=self.sign)
        self.hexy._act(movement)
        self.last_location = degrees

    def set_rel_position(self, degrees):
        base_position = self.last_location if self.last_location else 0
        self.set_abs_position(base_position + degrees)

    def goto_last_position(self):
        self.set_rel_position(0)

    def stop(self):
        self.hexy._stop(self.number)

    def center(self):
        self.set_abs_position(0)

class Leg(object):
    def __init__(self, hexy, servos, offsets=(0,0,0), signs=(1,1,1), lengths=(26,49,52), origin=(0,0,0), start_angles=(0,-45,-45)):
        construct = lambda i: Servo(hexy=hexy, number=servos[i], offset=offsets[i], sign=signs[i], start_angle=start_angles[i])
        self.hip_servo = construct(0)
        self.thigh_servo = construct(1)
        self.knee_servo = construct(2)
        self.servos = [self.hip_servo, self.thigh_servo, self.knee_servo]
        self.servo_map = {
            "hip":self.hip_servo,
            "thigh":self.thigh_servo,
            "knee":self.knee_servo
        }
        self.hip_length = lengths[0]
        self.thigh_length = lengths[1]
        self.knee_length = lengths[2]
        self.origin = origin

    def stop(self):
        for servo in self.servos:
            servo.stop()

    def goto_last_position(self):
        for servo in self.servos:
            servo.goto_last_position()

class Head(object):
    def __init__(self, hexy, servo=31, offset=0):
        self.servo = Servo(hexy=hexy, number=servo, offset=offset, sign=-1, start_angle=0)

    def look(self, degrees):
        '''-90 is all the way to the left, +90 is all the way to the right'''
        self.servo.set_abs_position(degrees)

    def turn(self, degrees):
        self.servo.set_rel_position(degrees)

    def stop(self):
        self.servo.stop()

    def goto_last_position(self):
        self.servo.goto_last_position()

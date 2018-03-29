#!/usr/bin/env python3

import argparse
from hexy import Hexy
from hexy import keys
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Determine servo offsets.')
    parser.add_argument("-i", "--input-file", dest="infile", default=None, help="File from which to load default offsets.  Optional.")
    parser.add_argument("-o", "--output-file", dest="outfile", default=None, help="File to which to write offsets at the end.  Optional.  They'll be printed to the screen regardless.")
    args = parser.parse_args()
    return args


description = '''This tool will help you calculate the necessary offset values to make all servos as precisely centered as possible.
Before the adjustment step for each servo, this tool will wiggle it slightly to make it abundantly clear which servo is being centered.
The left and right arrows will move the servo slightly, and update the offset.  That'll be displayed on the screen.
The up and down arrows will be used to adjust the sensitivity of the adjustments made by the L/R arrows.  UP increases the adjustment size, DOWN decreases it.
'''

print(description)

def _determine_offset(servo):
    print("Preparing to determine offset for servo #{}.  Press <enter> to wiggle and begin.  Press <tab> to skip.".format(servo.number))
    while True:
        arrow = keys.get_key()
        if arrow == keys.RETURN:
            break
        elif arrow == keys.TAB:
            return servo.offset
        else:
            pass
    servo.set_abs_position(15)
    servo.hexy._sleep(250)
    servo.set_abs_position(-15)
    servo.hexy._sleep(250)
    servo.set_abs_position(15)
    servo.hexy._sleep(250)
    servo.set_abs_position(-15)
    servo.hexy._sleep(250)
    servo.set_abs_position(0)
    print("Done wiggling.  Set to what you consider true center.")
    sensitivity = 0.5
    initial_offset = servo.offset
    while True:
        arrow = keys.get_key()
        if arrow == keys.RETURN:
            return servo.offset
        elif arrow == keys.UP:
            sensitivity = min(1, sensitivity + 0.1)
            print("Sensitivity: {:.1f}".format(sensitivity))
            continue
        elif arrow == keys.DOWN:
            sensitivity = max(0.1, sensitivity - 0.1)
            print("Sensitivity: {:.1f}".format(sensitivity))
            continue
        elif arrow == keys.RIGHT:
            print("Adding {:.1f} degree(s)".format(sensitivity))
            servo.offset += sensitivity
        elif arrow == keys.LEFT:
            print("Subtracting {:.1f} degree(s)".format(sensitivity))
            servo.offset -= sensitivity
        elif arrow == keys.CTRL_C:
            raise KeyboardInterrupt()
        else:
            print("Unknown key pressed.")
        servo.center()
        servo.hexy._sleep(50)

def determine_offset(servo):
    servo.stop()
    offset = _determine_offset(servo)
    servo.stop()
    print("Offset: {:.1f}".format(offset))
    return offset

args = parse_args()

offsets = {}
if args.infile:
    with open(args.infile) as f:
        offsets = json.load(f)

jeff = Hexy() # I've named my Hexy Jeff.  No particular reason, just seemed like a good name.
jeff.connect()
jeff.center()
jeff._sleep(250)
jeff.stop()

servo_map = {"Head":jeff.head.servo}
key_order = ["Head"]
for name in jeff.leg_map:
    leg = jeff.leg_map[name]
    for jname in leg.servo_map:
        servo_name = "{}/{}".format(name, jname)
        key_order.append(servo_name)
        servo_map[servo_name] = leg.servo_map[jname]

for key in key_order:
    print("Servo name: {}".format(key))
    servo = servo_map[key]
    servo.offset = offsets.get(str(servo.number), servo.offset)
    determine_offset(servo_map[key])

offsets = {s.number:s.offset for s in servo_map.values()}

print(json.dumps(offsets))
if args.outfile:
    with open(args.outfile, "w") as f:
        json.dump(offsets, f)

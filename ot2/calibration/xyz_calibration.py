import json
import serial,time
from opentrons import protocol_api, types

X_MIN = 10
X_MAX = 380
Y_MIN = 10
Y_MAX = 340
Z_MIN = 40
Z_MAX = 245

VIAL_NUM_STR = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

locationFile = open('vial_xy_location.txt', 'w+')
lines = locationFile.readlines()
locationFile.close()
xyCoordinates = []
for line in lines:
    if line != "\n":
        line = line.split(',')
        temp = [i.strip() for i in line]
        xyCoordinates.append([float(i) for i in temp])

NUM_VIALS = len(xyCoordinates)

metadata = {'apiLevel': '2.0'}

test_coordinates = types.Point(150,150,150)

def uniq(l):
    res = []
    for i in l:
        if i not in res:
            res.append(i)
    return res

def replace_txt_file_line(fileName, lineNum, coordinates):
    lines = open(fileName, 'r').readlines()
    lines[lineNum] = coordinates
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def calibrate_pre_wash_location():


def calibrate_post_wash_location():


def calibrate_bleach_location():


def calibrate_vial_location(vialNum, protocol):
    currentPosition = protocol._hw_manager.gantry_position(types.Mount.LEFT)
    currentX = "{:.2f}".format(currentPosition.x)
    currentY = "{:.2f}".format(currentPosition.y)
    currentZ = "{:.2f}".format(currentPosition.z)
    print("Current position of sampling head: x = ", currentX, " y = ", currentY, " z = ", currentZ)

    input_coordinates = [ float(x) for x in input().split() ]
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(input_coordinates[0],input_coordinates[1],input_coordinates[2]), speed=20)


def collect_sample(protocol):
    print("Collecting sample!")
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(100,200,245), speed=100)
    while True:
        vial = input("Enter vial name [0-14 = vial number, 'pre' = pre-wash bottle, 'post' = post-wash bottle, 'bl' = bleach bottle]: ")
        if vial == 'pre':    
            calibrate_pre_wash_location()
        elif vial == 'post':
            calibrate_post_wash_location()
        elif vial == 'bl':
            calibrate_bleach_location()
        elif vial in VIAL_NUM_STR:
            vialNum = int(vial)             
            calibrate_vial_location(vialNum)
        else:
            print("Wrong input. Try again.") 

        input_coordinates = [ float(x) for x in input().split() ]
        protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(input_coordinates[0],input_coordinates[1],input_coordinates[2]), speed=20)
    
#    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(100,350,30), speed=50)
    protocol._hw_manager.hardware.home()
    return 1

def run(protocol: protocol_api.ProtocolContext):
#    tiprack = protocol.load_labware(TIPRACK_LOADNAME, TIPRACK_SLOT)
#    pipette = protocol.load_instrument(PIPETTE_NAME, mount='left')
#    test_labware = protocol.load_labware_from_definition(
#        LABWARE_DEF,
#        TEST_LABWARE_SLOT,
#        LABWARE_LABEL,
#    )

#    num_cols = len(LABWARE_DEF.get('ordering', [[]]))
#    num_rows = len(LABWARE_DEF.get('ordering', [[]])[0])
#    well_locs = uniq([
#        'A1',
#        '{}{}'.format(chr(ord('A') + num_rows - 1), str(num_cols))])

#    pipette.pick_up_tip()

#    center_location = test_labware['A1'].center()
#    adjusted_location = center_location.move(types.Point(x=0,y=0,z=0))
#    loc2 = center_location.move(types.Point(x=20, y=20, z=0))    
#    loc3 = center_location.move(types.Point(x=0, y=20, z=0))
#    loc4 = center_location.move(types.Point(x=0, y=20, z=5))

#    def set_speeds(rate):
#        protocol.max_speeds.update({
#            'X': (600 * rate),
#            'Y': (400 * rate),
#            'Z': (125 * rate),
#            'A': (125 * rate),
#        })

#        speed_max = max(protocol.max_speeds.values())
#
#        for instr in protocol.loaded_instruments.values():
#            instr.default_speed = speed_max
#
#    set_speeds(RATE)

#    for slot in CALIBRATION_CROSS_SLOTS:
#        coordinate = CALIBRATION_CROSS_COORDS[slot]
#        location = types.Location(point=types.Point(**coordinate),
#                                  labware=None)
#        pipette.move_to(location)
#        protocol.pause(
#            f"Confirm {PIPETTE_MOUNT} pipette is at slot {slot} calibration cross")

#    pipette.home()
#    protocol.pause(f"Place your labware in Slot {TEST_LABWARE_SLOT}")
#    pipette.move_to(test_labware['A1'].top())
#    pipette.move_to(test_labware['A1'].top(-10))
#    pipette.move_to(adjusted_location)
#    pipette.move_to(loc2)
#    pipette.move_to(loc3)
#    pipette.move_to(loc4)
#    pipette.home()

#    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, test_coordinates, speed=100)
#    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(200,200,30), speed=50)
    if collect_sample(protocol):
        print("Done!")



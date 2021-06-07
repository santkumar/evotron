import json
import serial,time
from opentrons import protocol_api, types

CALIBRATION_CROSS_COORDS = {
    '1': {
        'x': 12.13,
        'y': 9.0,
        'z': 0.0
    },
    '3': {
        'x': 380.87,
        'y': 9.0,
        'z': 0.0
    },
    '7': {
        'x': 12.13,
        'y': 258.0,
        'z': 0.0
    }
}
CALIBRATION_CROSS_SLOTS = ['1', '3', '7']
TEST_LABWARE_SLOT = '2'

RATE = 0.25  # % of default speeds
SLOWER_RATE = 0.1

PIPETTE_MOUNT = 'left'
PIPETTE_NAME = 'p300_multi_gen2'

TIPRACK_SLOT = '5'
TIPRACK_LOADNAME = 'opentrons_96_tiprack_300ul'

LABWARE_DEF_JSON = """{"ordering":[["A1"]],"brand":{"brand":"CTSB_DBSSE_custom","brandId":[]},"metadata":{"displayName":"Custom Plate for eVOLVER","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.47,"zDimension":100},"wells":{"A1":{"depth":90,"totalLiquidVolume":20000,"shape":"rectangular","xDimension":127.76,"yDimension":85.47,"x":63.88,"y":42.73,"z":10}},"groups":[{"metadata":{"wellBottomShape":"flat"},"wells":["A1"]}],"parameters":{"format":"irregular","quirks":["centerMultichannelOnWells","touchTipDisabled"],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"custom_evolver"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""
LABWARE_DEF = json.loads(LABWARE_DEF_JSON)
LABWARE_LABEL = LABWARE_DEF.get('metadata', {}).get(
    'displayName', 'test labware')

metadata = {'apiLevel': '2.0'}


def uniq(l):
    res = []
    for i in l:
        if i not in res:
            res.append(i)
    return res


def run(protocol: protocol_api.ProtocolContext):
#    tiprack = protocol.load_labware(TIPRACK_LOADNAME, TIPRACK_SLOT)
    pipette = protocol.load_instrument(PIPETTE_NAME, mount='left')
    test_labware = protocol.load_labware_from_definition(
        LABWARE_DEF,
        TEST_LABWARE_SLOT,
        LABWARE_LABEL,
    )

#    num_cols = len(LABWARE_DEF.get('ordering', [[]]))
#    num_rows = len(LABWARE_DEF.get('ordering', [[]])[0])
#    well_locs = uniq([
#        'A1',
#        '{}{}'.format(chr(ord('A') + num_rows - 1), str(num_cols))])

#    pipette.pick_up_tip()

    center_location = test_labware['A1'].center()
    adjusted_location = center_location.move(types.Point(x=0,y=0,z=0))
    loc2 = center_location.move(types.Point(x=20, y=20, z=0))    
    loc3 = center_location.move(types.Point(x=0, y=20, z=0))
    loc4 = center_location.move(types.Point(x=0, y=20, z=5))

    def set_speeds(rate):
        protocol.max_speeds.update({
            'X': (600 * rate),
            'Y': (400 * rate),
            'Z': (125 * rate),
            'A': (125 * rate),
        })

        speed_max = max(protocol.max_speeds.values())

        for instr in protocol.loaded_instruments.values():
            instr.default_speed = speed_max

    set_speeds(RATE)

#    for slot in CALIBRATION_CROSS_SLOTS:
#        coordinate = CALIBRATION_CROSS_COORDS[slot]
#        location = types.Location(point=types.Point(**coordinate),
#                                  labware=None)
#        pipette.move_to(location)
#        protocol.pause(
#            f"Confirm {PIPETTE_MOUNT} pipette is at slot {slot} calibration cross")

    pipette.home()
#    protocol.pause(f"Place your labware in Slot {TEST_LABWARE_SLOT}")
    pipette.move_to(test_labware['A1'].top())
    pipette.move_to(test_labware['A1'].top(-10))
    pipette.move_to(adjusted_location)
    pipette.move_to(loc2)
    pipette.move_to(loc3)
    pipette.move_to(loc4)
    pipette.home()

    protocol._hw_manager.hardware.move_to(types.Mount.RIGHT, types.Point(200,200,100), speed=100)

    print('Running!')
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    cmd = input("Enter command : ")
                    arduino.write(cmd.encode())
                    while arduino.inWaiting()==0: pass
                    if arduino.inWaiting()>0:
                        answer = arduino.readline()
                        print(answer)
                        arduino.flushInput()
            except KeyboardInterrupt:
                print("Keyboard interrupt has been caught!")


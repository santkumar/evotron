import json
import serial,time
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.0'}

xy_locationVial1 = types.Point(200,200,245)
z_locationVial1 = types.Point(200,200,30)
dippingTimeSeconds = 5
xySpeed = 100
zSpeed = 50
cmdMoveNeedleForSampling = "mnfs?"
cmdDone = "d?"
cmdError = "err?"

def collect_sample(protocol):
    print("Collecting sample!")
    protocol._hw_manager.hardware.home()
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationVial1, speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, z_locationVial1, speed=zSpeed)
    time.sleep(dippingTimeSeconds)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationVial1, speed=zSpeed)
    protocol._hw_manager.hardware.home()
    return 1

def run(protocol: protocol_api.ProtocolContext):

    print('Running!')
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    while arduino.inWaiting()==0: pass
                    if arduino.inWaiting()>0:
                        inputStringArduino = arduino.readline()
                        print(inputStringArduino)
                        if inputStringArduino == cmdMoveNeedleForSampling:
                            if collect_sample(protocol):
                                arduino.write(cmdDone)
                            else :
                                arduino.write(cmdError)
                        arduino.flushInput()
            except KeyboardInterrupt:
                print("Keyboard interrupt has been caught!")


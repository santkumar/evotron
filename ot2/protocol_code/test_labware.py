import json
import serial,time
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.0'}

xy_locationVial1 = types.Point(200,200,245)
z_locationVial1 = types.Point(200,200,30)

def collect_sample

def run(protocol: protocol_api.ProtocolContext):

    protocol._hw_manager.hardware.home()
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


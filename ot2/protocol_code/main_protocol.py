import json
import serial,time
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.0'}

xy_locationVial1 = types.Point(187,70.5,245)
z_locationVial1 = types.Point(187,70.5,40)

xy_locationPreWash = types.Point(367,52,245)
z_locationPreWash = types.Point(367,52,90)

xy_locationBleach = types.Point(367,140,245)
z_locationBleach = types.Point(367,140,90)

xy_locationPostWash = types.Point(362,230,245)
z_locationPostWash = types.Point(362,230,90)

xySpeed = 100
zSpeed = 50

sampleDippingTimeSeconds = 3
preWashDippingTimeSeconds = 4
bleachDippingTimeSeconds = 6
postWashDippingTimeSeconds = 8

IS_NEEDLE_CLEAN = 1
PRE_WASH_DONE = 0
BLEACH_DONE = 0
POST_WASH_DONE = 0

cmdError = "!err?"

cmdMoveNeedleForSampling = "!mns?"
cmdDoneMoveNeedleForSampling = "!dmn?"

cmdStartPreWash = "!spr?"
cmdDonePreWash = "!dpr?"

cmdStartBleach = "!sbl?"
cmdDoneBleach = "!dbl?"

cmdStartPostWash = "!spo?"
cmdDonePostWash = "!dpo?"


def collect_sample(protocol,arduino):
    print("Collecting sample!")
    protocol._hw_manager.hardware.home()
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationVial1, speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, z_locationVial1, speed=zSpeed)
    time.sleep(sampleDippingTimeSeconds)
    arduino.write(cmdDoneMoveNeedleForSampling.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationVial1, speed=zSpeed)
    # protocol._hw_manager.hardware.home()
    return 1

def pre_wash(protocol,arduino):
    print("Started pre-wash") 
    # protocol._hw_manager.hardware.home()
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationPreWash, speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, z_locationPreWash, speed=zSpeed)
    time.sleep(preWashDippingTimeSeconds)
    arduino.write(cmdDonePreWash.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationPreWash, speed=zSpeed)
    return 1

def bleach(protocol,arduino):
    print("Started bleach") 
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationBleach, speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, z_locationBleach, speed=zSpeed)
    time.sleep(bleachDippingTimeSeconds)
    arduino.write(cmdDoneBleach.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationBleach, speed=zSpeed)
    return 1

def post_wash(protocol,arduino):
    print("Started post-wash") 
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationPostWash, speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, z_locationPostWash, speed=zSpeed)
    time.sleep(postWashDippingTimeSeconds)
    arduino.write(cmdDonePostWash.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, xy_locationPostWash, speed=zSpeed)
    protocol._hw_manager.hardware.home()
    return 1

def run(protocol: protocol_api.ProtocolContext):

    global IS_NEEDLE_CLEAN
    global PRE_WASH_DONE
    global BLEACH_DONE
    global POST_WASH_DONE

    print('Running!')
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            arduino.flush()
            try:
                while True:
                    while arduino.inWaiting()==0: pass
                    if arduino.inWaiting()>0:
                        inputStringArduino = arduino.readline()
                        print(inputStringArduino.decode('utf-8'))
                        if ((inputStringArduino.decode('utf-8') == cmdMoveNeedleForSampling) and (IS_NEEDLE_CLEAN == 1)):
                            if collect_sample(protocol,arduino):
                                IS_NEEDLE_CLEAN = 0
                                # arduino.write(cmdDoneMoveNeedleForSampling.encode())
                            else :
                                IS_NEEDLE_CLEAN = 0 # do cleaning again just to be sure
                                arduino.write(cmdError.encode())
                        elif ((inputStringArduino.decode('utf-8') == cmdStartPreWash) and (IS_NEEDLE_CLEAN == 0) and (PRE_WASH_DONE == 0)):
                            if pre_wash(protocol,arduino):
                                PRE_WASH_DONE = 1
                                # arduino.write(cmdDonePreWash.encode())
                            else :
                                PRE_WASH_DONE = 0
                                arduino.write(cmdError.encode())
                        elif ((inputStringArduino.decode('utf-8') == cmdStartBleach) and (PRE_WASH_DONE == 1) and (BLEACH_DONE == 0)):
                            if bleach(protocol,arduino):
                                BLEACH_DONE = 1
                                # arduino.write(cmdDoneBleach.encode())
                            else :
                                BLEACH_DONE = 0
                                arduino.write(cmdError.encode())
                        elif ((inputStringArduino.decode('utf-8') == cmdStartPostWash) and (BLEACH_DONE == 1) and (POST_WASH_DONE == 0)):
                            if post_wash(protocol,arduino):
                                IS_NEEDLE_CLEAN = 1
                                PRE_WASH_DONE = 0
                                BLEACH_DONE = 0
                                POST_WASH_DONE = 0
                                # arduino.write(cmdDonePostWash.encode())
                            else :
                                POST_WASH_DONE = 0
                                arduino.write(cmdError.encode())
                        arduino.flushInput()
            except KeyboardInterrupt:
                print("Keyboard interrupt has been caught!")

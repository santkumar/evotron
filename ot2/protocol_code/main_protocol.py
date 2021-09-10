import json
import serial,time
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.0'}

z_top = 245
z_sample = 40
z_wash = 90

xy_preWash = [367,52]
xy_bleach = [369,142]
xy_postWash = [362,233]

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
SAMPLING_CMD_RECEIVED = 0

NUM_VIALS = 1

cmdError = "!err?"

cmdMoveNeedleForSampling = "!mns?"
cmdWhichVial = "!whv?"
cmdDoneMoveNeedleForSampling = "!dmn?"

cmdStartPreWash = "!spr?"
cmdDonePreWash = "!dpr?"

cmdStartBleach = "!sbl?"
cmdDoneBleach = "!dbl?"

cmdStartPostWash = "!spo?"
cmdDonePostWash = "!dpo?"


def collect_sample(protocol,arduino,xCoord,yCoord):
    print("Collecting sample!")
    protocol._hw_manager.hardware.home()
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xCoord,yCoord,z_top), speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xCoord,yCoord,z_sample), speed=zSpeed)
    time.sleep(sampleDippingTimeSeconds)
    arduino.write(cmdDoneMoveNeedleForSampling.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xCoord,yCoord,z_top), speed=zSpeed)
    # protocol._hw_manager.hardware.home()
    return 1

def pre_wash(protocol,arduino):
    print("Started pre-wash") 
    # protocol._hw_manager.hardware.home()
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_preWash[0],xy_preWash[1],z_top), speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_preWash[0],xy_preWash[1],z_wash), speed=zSpeed)
    time.sleep(preWashDippingTimeSeconds)
    arduino.write(cmdDonePreWash.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_preWash[0],xy_preWash[1],z_top), speed=zSpeed)
    return 1

def bleach(protocol,arduino):
    print("Started bleach") 
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_bleach[0],xy_bleach[1],z_top), speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_bleach[0],xy_bleach[1],z_wash), speed=zSpeed)
    time.sleep(bleachDippingTimeSeconds)
    arduino.write(cmdDoneBleach.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_bleach[0],xy_bleach[1],z_top), speed=zSpeed)
    return 1

def post_wash(protocol,arduino):
    print("Started post-wash") 
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_postWash[0],xy_postWash[1],z_top), speed=xySpeed)
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_postWash[0],xy_postWash[1],z_wash), speed=zSpeed)
    time.sleep(postWashDippingTimeSeconds)
    arduino.write(cmdDonePostWash.encode())
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(xy_postWash[0],xy_postWash[1],z_top), speed=zSpeed)
    protocol._hw_manager.hardware.home()
    return 1

def run(protocol: protocol_api.ProtocolContext):

    global IS_NEEDLE_CLEAN
    global PRE_WASH_DONE
    global BLEACH_DONE
    global POST_WASH_DONE
    global NUM_VIALS
    global SAMPLING_CMD_RECEIVED

    locationFile = open('vial_xy_location.txt', 'r')
    lines = locationFile.readlines()
    locationFile.close()
    xyCoordinates = []
    for line in lines:
        if line != "\n":
            line = line.split(',')
            temp = [i.strip() for i in line]
            xyCoordinates.append([float(i) for i in temp])

    NUM_VIALS = len(xyCoordinates)

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
                        if ((inputStringArduino.decode('utf-8') == cmdMoveNeedleForSampling) and (IS_NEEDLE_CLEAN == 1) and (SAMPLING_CMD_RECEIVED == 0)):
                            SAMPLING_CMD_RECEIVED = 1
                            arduino.write(cmdWhichVial.encode())
                        elif ((IS_NEEDLE_CLEAN == 1) and (SAMPLING_CMD_RECEIVED == 1)):
                            receivedData = inputStringArduino.decode('utf-8','ignore')
                            vialNum = int(receivedData.strip());    
                            if collect_sample(protocol,arduino,xyCoordinates[vialNum][0],xyCoordinates[vialNum][1]):
                                IS_NEEDLE_CLEAN = 0
                                SAMPLING_CMD_RECEIVED = 0
                                # arduino.write(cmdDoneMoveNeedleForSampling.encode())
                            else :
                                IS_NEEDLE_CLEAN = 0 # do cleaning again just to be sure
                                SAMPLING_CMD_RECEIVED = 0
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

import json
import serial,time
# from pynput import keyboard
import os
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.0'}

def take_user_input_and_move(protocol):
    print("Calibration mode: Be careful while typing coordinates. Right now, there is no fail safe against sampling needle hitting the vials. This will be handled in further releases.")
    protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(100,100,245), speed=100)
#    check1 = protocol._hw_manager.hardware.gantry_position(types.Mount.LEFT)
#    check1 = protocol._hw_manager.hardware.current_position(types.Mount.LEFT)
#    check2 = "{:.2f}".format(check1.x)
#    print(check2)	
    while True:
        print("Enter xyz coordinates with space in between and then press enter. For example: 200 100 245 (Here, 200 is X, 100 is Y and 245 is Z coordinate).")
        input_coordinates = [ float(x) for x in input().split() ]
        protocol._hw_manager.hardware.move_to(types.Mount.LEFT, types.Point(input_coordinates[0],input_coordinates[1],input_coordinates[2]), speed=50)
    
    protocol._hw_manager.hardware.home()
    return 1

def run(protocol: protocol_api.ProtocolContext):
#    protocol._hw_manager.hardware.set_lights(rails=True)     
#    print("Lights!")
    if take_user_input_and_move(protocol):
        print("Done!")


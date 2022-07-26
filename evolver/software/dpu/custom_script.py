#!/usr/bin/env python3

import numpy as np
import logging
import os.path
import time

# logger setup
logger = logging.getLogger(__name__)

##### USER DEFINED GENERAL SETTINGS #####

#To change each experiment:
# EXP_NAME (has to end in _expt)
# TEMP_INITIAL (put 20 for vials that should't be heated)
# STIR_INITIAL (8 for stirring, 0 otherwise)
# VOLUME (20ml is standard)
# LED1_PWM_VALUES_INITIAL (Initial blue light intensity)
# turbidostat_vials (need to write a list with the vial numbers for which turbidostat regulation will be active)
# lower_thresh and upper_thresh (OD Thresholds for turbidostat regulation. Write 9999 in vials without turbidostat regulation)

#set new name for each experiment, otherwise files will be overwritten 
EXP_NAME = '20220505_bJAG132_237_ClosedLoop_132_235OpenLoop120Light_expt'
EVOLVER_IP = '192.168.1.2'
EVOLVER_PORT = 8081

##### Identify pump calibration files, define initial values for temperature, stirring, volume, power settings

#TEMP_INITIAL = [30] * 16 #degrees C, makes 16-value list
#Alternatively enter 16-value list to set different values (20 means no temp regulation, reference values found on the right)
TEMP_INITIAL = [37.1,\
                37.2,\
                37.5,\
                20,\
                20,\
                20,\
                37.8,\
                20,\
                20,\
                37,\
                20,\
                20,\
                20,\
                20,\
                20,\
                20]
# TEMP_INITIAL = [0 --- 37.1,
               # 1 --- 37.2,
               # 2 --- 37.5,
               # 3 --- 37.2,
               # 4 --- 36.9,
               # 5 --- 37,
               # 6 --- 37.8,
               # 7 --- 37.1,
               # 8 --- 36.8,
               # 9 --- 37,
               # 10 --- 36.6,
               # 11 --- 38,
               # 12 --- 37.2,
               # 13 --- 37.1,
               # 14 --- 37,
               # 15 --- 20]

#STIR_INITIAL = [8] * 16 #try 8,10,12 etc; makes 16-value list
#Alternatively enter 16-value list to set different values
STIR_INITIAL = [8,\
                8,\
                8,\
                0,\
                0,\
                0,\
                8,\
                0,\
                0,\
                8,\
                0,\
                0,\
                0,\
                0,\
                0,\
                0]  

VOLUME =  20 #mL, determined by vial cap straw length
PUMP_CAL_FILE = 'pump_cal.txt' #tab delimited, mL/s with 16 influx pumps on first row, etc.
OPERATION_MODE = 'turbidostat' #use to choose between 'turbidostat' and 'chemostat' functions
# if using a different mode, name your function as the OPERATION_MODE variable

#PWM Values for Opto LED1 2850
LED1_PWM_VALUES_INITIAL = [0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          2170,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0,\
                          0]  
# LED1_PWM_VALUES_INITIAL = [0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0,\
                           # 0] 
LED1_PWM_VALUES_RUNNING = LED1_PWM_VALUES_INITIAL

##### END OF USER DEFINED GENERAL SETTINGS #####

def turbidostat(eVOLVER, input_data, vials, elapsed_time):
    OD_data = input_data['transformed']['od']

    ##### USER DEFINED VARIABLES #####

    turbidostat_vials = [0,1,2,6,9] #vials is all 16, can set to different range (ex. [0,1,2,3]) to only trigger tstat on those vials
    stop_after_n_curves = np.inf #set to np.inf to never stop, or integer value to stop diluting after certain number of growth curves

    #lower_thresh = [0.2] * len(vials) #to set all vials to the same value, creates 16-value list
    #upper_thresh = [0.4] * len(vials) #to set all vials to the same value, creates 16-value list
    #Alternatively, use 16 value list to set different thresholds, use 9999 for vials not being used
    #               0      1      2      3      4      5      6      7      8      9      10     11     12     13     14     15
    lower_thresh = [0.100, 0.100, 0.100, 99999, 99999, 99999, 0.100, 99999, 99999, 0.100, 99999, 99999, 99999, 99999, 99999, 99999]
    upper_thresh = [0.150, 0.150, 0.150, 99999, 99999, 99999, 0.150, 99999, 99999, 0.150, 99999, 99999, 99999, 99999, 99999, 99999]
    
    ##### END OF USER DEFINED VARIABLES #####


    ##### Turbidostat Settings #####
    #Tunable settings for overflow protection, pump scheduling etc. Unlikely to change between expts

    time_out = 5 #(sec) additional amount of time to run efflux pump
    pump_wait = 1 # (min) minimum amount of time to wait between pump events

    ##### End of Turbidostat Settings #####

    save_path = os.path.dirname(os.path.realpath(__file__)) #save path
    flow_rate = eVOLVER.get_flow_rate() #read from calibration file

    ##### Running LED1 PWM input values #####
    global LED1_PWM_VALUES_RUNNING
    
    ##### Turbidostat Control Code Below #####

    # fluidic message: initialized so that no change is sent
    MESSAGE = ['--'] * 48
    
    UPDATE_LED1_PWM = 0
    for x in turbidostat_vials: #main loop through each vial

        # Update turbidostat configuration files for each vial
        # initialize OD and find OD path

        file_name =  "vial{0}_ODset.txt".format(x)
        ODset_path = os.path.join(save_path, EXP_NAME, 'ODset', file_name)
        data = np.genfromtxt(ODset_path, delimiter=',')
        ODset = data[len(data)-1][1]
        ODsettime = data[len(data)-1][0]
        num_curves=len(data)/2;
        
        file_name =  "vial{0}_OD.txt".format(x)
        OD_path = os.path.join(save_path, EXP_NAME, 'OD', file_name)
        data = np.genfromtxt(OD_path, delimiter=',')
        average_OD = 0

        # Determine whether turbidostat dilutions are needed
        enough_ODdata = (len(data) > 7) #logical, checks to see if enough data points (couple minutes) for sliding window
        collecting_more_curves = (num_curves <= (stop_after_n_curves + 2)) #logical, checks to see if enough growth curves have happened

        if enough_ODdata:
            # Take median to avoid outlier
            od_values_from_file = []
            for n in range(1,7):
                od_values_from_file.append(data[len(data)-n][1])
            average_OD = float(np.median(od_values_from_file))

            #if recently exceeded upper threshold, note end of growth curve in ODset, allow dilutions to occur and growthrate to be measured
            if (average_OD > upper_thresh[x]) and (ODset != lower_thresh[x]):
                text_file = open(ODset_path, "a+")
                text_file.write("{0},{1}\n".format(elapsed_time,
                                                   lower_thresh[x]))
                text_file.close()
                ODset = lower_thresh[x]
                # calculate growth rate
                eVOLVER.calc_growth_rate(x, ODsettime, elapsed_time)

            #if have approx. reached lower threshold, note start of growth curve in ODset
            if (average_OD < (lower_thresh[x] + (upper_thresh[x] - lower_thresh[x]) / 3)) and (ODset != upper_thresh[x]):
                text_file = open(ODset_path, "a+")
                text_file.write("{0},{1}\n".format(elapsed_time, upper_thresh[x]))
                text_file.close()
                ODset = upper_thresh[x]

            #if need to dilute to lower threshold, then calculate amount of time to pump
            if average_OD > ODset and collecting_more_curves:

                time_in = - (np.log(lower_thresh[x]/average_OD)*VOLUME)/flow_rate[x]

                if time_in > 20:
                    time_in = 20

                time_in = round(time_in, 2)

                file_name =  "vial{0}_pump_log.txt".format(x)
                file_path = os.path.join(save_path, EXP_NAME,
                                         'pump_log', file_name)
                data = np.genfromtxt(file_path, delimiter=',')
                last_pump = data[len(data)-1][0]
                if ((elapsed_time - last_pump)*60) >= pump_wait: # if sufficient time since last pump, send command to Arduino
                    logger.info('turbidostat dilution for vial %d' % x)
                    # influx pump
                    MESSAGE[x] = str(time_in)
                    # efflux pump
                    MESSAGE[x + 16] = str(time_in + time_out)

                    file_name =  "vial{0}_pump_log.txt".format(x)
                    file_path = os.path.join(save_path, EXP_NAME, 'pump_log', file_name)

                    text_file = open(file_path, "a+")
                    text_file.write("{0},{1}\n".format(elapsed_time, time_in))
                    text_file.close()
                    
        else:
            logger.debug('not enough OD measurements for vial %d' % x)

        file_name =  "vial{0}_LED1_input.txt".format(x)
        file_path = os.path.join(save_path, EXP_NAME, 'LED1_input', file_name)
        data = np.genfromtxt(file_path, delimiter=',')
        pwm_input = data[len(data)-1][1]
        if pwm_input != LED1_PWM_VALUES_RUNNING[x]: 
            LED1_PWM_VALUES_RUNNING[x] = pwm_input
            UPDATE_LED1_PWM = 1
            text_file = open(file_path, "a+")
            text_file.write("{0},{1}\n".format(elapsed_time, pwm_input))
            text_file.close()

    # send fluidic command only if we are actually turning on any of the pumps
    if MESSAGE != ['--'] * 48:
        eVOLVER.fluid_command(MESSAGE)

    if UPDATE_LED1_PWM != 0:
        eVOLVER.update_opto_led1_intensity(LED1_PWM_VALUES_RUNNING)

        # your_FB_function_here() #good spot to call feedback functions for dynamic temperature, stirring, etc for ind. vials
    # your_function_here() #good spot to call non-feedback functions for dynamic temperature, stirring, etc.

    # end of turbidostat() fxn

def chemostat(eVOLVER, input_data, vials, elapsed_time):
    OD_data = input_data['transformed']['od_90']

    ##### USER DEFINED VARIABLES #####
    start_OD = 0 # ~OD600, set to 0 to start chemostate dilutions at any positive OD
    start_time = 0 #hours, set 0 to start immediately
    # Note that script uses AND logic, so both start time and start OD must be surpassed

    chemostat_vials = vials #vials is all 16, can set to different range (ex. [0,1,2,3]) to only trigger tstat on those vials

    rate_config = [0.5] * 16 #to set all vials to the same value, creates 16-value list
    #UNITS of 1/hr, NOT mL/hr, rate = flowrate/volume, so dilution rate ~ growth rate, set to 0 for unused vials

    #Alternatively, use 16 value list to set different rates, use 0 for vials not being used
    #rate_config = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]

    ##### END OF USER DEFINED VARIABLES #####


    ##### Chemostat Settings #####

    #Tunable settings for bolus, etc. Unlikely to change between expts
    bolus = 0.5 #mL, can be changed with great caution, 0.2 is absolute minimum

    ##### End of Chemostat Settings #####

    save_path = os.path.dirname(os.path.realpath(__file__)) #save path
    flow_rate = eVOLVER.get_flow_rate() #read from calibration file
    period_config = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #initialize array
    bolus_in_s = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #initialize array


    ##### Chemostat Control Code Below #####

    for x in chemostat_vials: #main loop through each vial

        # Update chemostat configuration files for each vial

        #initialize OD and find OD path
        file_name =  "vial{0}_OD.txt".format(x)
        OD_path = os.path.join(save_path, EXP_NAME, 'OD', file_name)
        data = np.genfromtxt(OD_path, delimiter=',')
        average_OD = 0
        enough_ODdata = (len(data) > 7) #logical, checks to see if enough data points (couple minutes) for sliding window

        if enough_ODdata: #waits for seven OD measurements (couple minutes) for sliding window

            #calculate median OD
            od_values_from_file = []
            for n in range(1, 7):
                od_values_from_file.append(data[len(data)-n][1])
            average_OD = float(np.median(od_values_from_file))

            # set chemostat config path and pull current state from file
            file_name =  "vial{0}_chemo_config.txt".format(x)
            chemoconfig_path = os.path.join(save_path, EXP_NAME,
                                            'chemo_config', file_name)
            chemo_config = np.genfromtxt(chemoconfig_path, delimiter=',')
            last_chemoset = chemo_config[len(chemo_config)-1][0] #should t=0 initially, changes each time a new command is written to file
            last_chemophase = chemo_config[len(chemo_config)-1][1] #should be zero initially, changes each time a new command is written to file
            last_chemorate = chemo_config[len(chemo_config)-1][2] #should be 0 initially, then period in seconds after new commands are sent

            # once start time has passed and culture hits start OD, if no command has been written, write new chemostat command to file
            if ((elapsed_time > start_time) & (average_OD > start_OD)):

                #calculate time needed to pump bolus for each pump
                bolus_in_s[x] = bolus/flow_rate[x]

                # calculate the period (i.e. frequency of dilution events) based on user specified growth rate and bolus size
                if rate_config[x] > 0:
                    period_config[x] = (3600*bolus)/((rate_config[x])*VOLUME) #scale dilution rate by bolus size and volume
                else: # if no dilutions needed, then just loops with no dilutions
                    period_config[x] = 0

                if  (last_chemorate != period_config[x]):
                    print('Chemostat updated in vial {0}'.format(x))
                    logger.info('chemostat initiated for vial %d, period %.2f'
                                % (x, period_config[x]))
                    # writes command to chemo_config file, for storage
                    text_file = open(chemoconfig_path, "a+")
                    text_file.write("{0},{1},{2}\n".format(elapsed_time,
                                                           (last_chemophase+1),
                                                           period_config[x])) #note that this changes chemophase
                    text_file.close()
        else:
            logger.debug('not enough OD measurements for vial %d' % x)

        # your_FB_function_here() #good spot to call feedback functions for dynamic temperature, stirring, etc for ind. vials
    # your_function_here() #good spot to call non-feedback functions for dynamic temperature, stirring, etc.

    eVOLVER.update_chemo(input_data, chemostat_vials, bolus_in_s, period_config) #compares computed chemostat config to the remote one
    # end of chemostat() fxn

# def your_function_here(): # good spot to define modular functions for dynamics or feedback

if __name__ == '__main__':
    print('Please run eVOLVER.py instead')

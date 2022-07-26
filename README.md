# evotron
Opentron OT-2 based automated sampling device for eVOLVER

## Preparation (summary)

* Hardware modifications: OT-2 sampling needle and tubings, eVOLVER modifications, Arduino 2560 Mega and pumps (sampling and waste-removal peristaltic pumps) integration 
* Save OT-2 protocol routines in the OT-2 raspberry pi system and run calibration to find location coordinates or vials and cleaning solution bottles (check ot2 folder).
* Modify eVOLVER dpu and conf.yml files (check evolver folder).
* Compile and upload the required code on Arduino 2560 Mega (check arduino folder).
* Prepare cytoflex experiment files and routines (check cytoflex folder).
* Modify MATLAB main file as per experiment (check matlab folder).

## To run

* First, run the eVOLVER experiment run routine (check eVOLVER manufacturer's instruction manual)
* In the MATLAB main.m file, modify **evolverExptDir** variable to the eVOLVER experiment folder location name. Modify other user input variables as required.
* Start MATLAB application as administrator. Run MATLAB main.m script.

**To get vials and sampling bottle locations on the OT-2 deck**

* Save *get_xyz_location.py* in */data/custom_protocols/* folder on the OT-2 raspberry pi system
* SSH into the OT-2 raspberry pi system
* Execute command: **cd /data/custom_protocols**
* Execute command: **opentrons_execute get_xyz_location.py**
* Enter the xyz coordinates as asked. Once the xy coordinate (such that the sampling needle can be lowered into the culture passing through the cap hole) of Vial #N has been found, note down the xy coordinates and then move to other vials. Same for the cleaning solution bottles.
* The xy coordinates of all the vials should be manually entered into **/data/custom_protocols/vial_xy_location.txt** file in ascending order in successive lines. The X and Y coordinates should be separated with a comma in the .txt file.
* The xy coordinates of cleaning solution bottles should be manually entered into **/data/custom_protocols/main_protocol.py** file as **xy_preWash**, **xy_bleach** and **xy_postWash** variables.
* Once all the desired locations have been found, press Ctrl + C.

**NOTE: Be careful while entering location coordinates. Any mistake might lead to sampling needle hitting the vials, cleaning bottles, or the OT-2 deck. A fail safe against these scenarios will be added in future releases.**     

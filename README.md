# Thesis source codes. 

---

## [automation_tools](https://github.com/amatanat/thesis/tree/master/automation_tools)

Folder contains the following scripts:
- [Tool](https://github.com/amatanat/thesis/blob/master/automation_tools/automated_tool_device.sh) for the Android device that performs the following steps: 
    - backup the currect state of a device
    - extract FS metadata
    - call python script
    - extract FS metadata
    - restore the backup
    
    Example configuration file for the tool can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/config.conf.example). We have used this tool to extract XML dumps before and after implementing a user action (CSM, CSP, FM, FP, OC) in WhatsApp in an Android device.

- [Tool](https://github.com/amatanat/thesis/blob/master/automation_tools/automated_tool_device_emulator.sh) that is similar to the above one. However, it calls an [emulator script](https://github.com/amatanat/thesis/blob/master/automation_tools/send_message_emulator.sh) after extracting FS metadata. Example configuration file for the tool can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/config_2.conf.example). We have used this tool to extract XML dumps before and after implementing a user action (RM, RP, PN, PN-text) in WhatsApp in an Android device. 
The [emulator script](https://github.com/amatanat/thesis/blob/master/automation_tools/send_message_emulator.sh) is used to start an emulator, run passed python script and kill an emulator. Example configuration file for the emulator script can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/emulator.conf.example).

- Used OpenRecoveryScripts can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/openrecoveryscript) and [here](https://github.com/amatanat/thesis/blob/master/automation_tools/openrecoveryscript2).




License
-------

 Copyright 2018 Matanat Ahmadova

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

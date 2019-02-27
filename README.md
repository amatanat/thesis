# Thesis source codes

---

## Fingerprint generation for third-party applications

- [Extract fingerprints](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/device_app_fingerprints_extractor.sh) of third-party applications those are installed to a device.
- [Insert](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/fingerprint_generation.py) extracted fingerprints into a [fingerprints DB](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/fingerprints.db).
- [Evaluate](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/evaluate_fingerprints_db.py) [fingerprints DB](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/fingerprints.db). 
  - Evaluation [results](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/evaluation_result.txt).
  
## Match installed applications in FBE 

- [Bash script](https://github.com/amatanat/thesis/blob/master/matcher/matcher.sh) is used to extract the FS metadata to an XML file and then call the [matcher script](https://github.com/amatanat/thesis/blob/master/matcher/identify_installed_apps.py) by passing extracting XML dump.
- [matcher script](https://github.com/amatanat/thesis/blob/master/matcher/identify_installed_apps.py) performs the following steps:
  1. This [script](https://github.com/amatanat/thesis/blob/master/matcher/xml_fingerprints_extractor.py) is used to extract fingerprints of applications from an XML dump.
  2. Then, extracted data is matched with the [fingerprints DB](https://github.com/amatanat/thesis/blob/master/fingerprint_generation/fingerprints.db).
  
  Example configuration file for the matcher script can be found [here](https://github.com/amatanat/thesis/blob/master/matcher/example_matcher_config.conf).

- Evaluation of fingerprints matching
  - [This folder](https://github.com/amatanat/thesis/tree/master/matcher/automated_evaluation) contains all the required scripts and evaluation results. 
    - [Script](https://github.com/amatanat/thesis/blob/master/matcher/automated_evaluation/evaluate_matcher_result.py)  to evaluate the matcher result.
    - [First](https://github.com/amatanat/thesis/tree/master/matcher/automated_evaluation/evaluation-1), [second](https://github.com/amatanat/thesis/tree/master/matcher/automated_evaluation/evaluation-2) and [third](https://github.com/amatanat/thesis/tree/master/matcher/automated_evaluation/evaluation-3) evaluation experiments.
    - Other evaluation [experiments](https://github.com/amatanat/thesis/tree/master/matcher/evaluation).
  
  

## WhatsApp UI automation

- [AndroidViewClient](https://github.com/dtmilano/AndroidViewClient/wiki) UI automation scripts:
   - conversation-send-message
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/conversation-send-message.py) when only one device is connected.
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/conversation-send-message-device_id.py) when more devices are connected.
   - conversation-send-photo
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/conversation-send-photo.py) when only one device is connected. Screen [video record](https://github.com/amatanat/thesis/blob/master/whatsapp/conversation-send-photo.webm) of the device while running the script.
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/conversation-send-photo-device_id.py) when more devices are connected.
   - fab-message
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/fab-message.py).
     - Screen [video record](https://github.com/amatanat/thesis/blob/master/whatsapp/fab-message.webm) of the device while running the script.
   - [fab-photo](https://github.com/amatanat/thesis/blob/master/whatsapp/fab-photo.py).
   - [open-close](https://github.com/amatanat/thesis/blob/master/whatsapp/open-close.py)
   - push-notification
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/push-notification.py).
     - Screen [video record](https://github.com/amatanat/thesis/blob/master/whatsapp/push-notification.webm) of the device while running the script.
   - receive-message
     - used [script](https://github.com/amatanat/thesis/blob/master/whatsapp/receive-messages.py).
     - Screen [video record](https://github.com/amatanat/thesis/blob/master/whatsapp/receive-message.webm) of the device while running the script.
- [monkeyrunner](https://developer.android.com/studio/test/monkeyrunner/) conversation-send-message [implementation](https://github.com/amatanat/thesis/blob/master/whatsapp/whatsapp-monkeyrunner.py). 
- :exclamation:  AndroidViewClient is used in our experiments. Used log configuration file can be found [here](https://github.com/amatanat/thesis/blob/master/whatsapp/logging.conf). 

## [automation_tools](https://github.com/amatanat/thesis/tree/master/automation_tools)

Folder contains the following scripts:
- [Tool](https://github.com/amatanat/thesis/blob/master/automation_tools/automated_tool_device.sh) for the Android device that performs the following steps: 
    - backup the currect state of a device
    - extract FS metadata
    - call python script
    - extract FS metadata
    - restore the backup
    
    Example configuration file for the tool can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/config.conf.example). We have used this tool to extract XML dumps before and after implementing a user action (CSM, CSP, FM, FP, OC) in WhatsApp in an Android device.

- [Tool](https://github.com/amatanat/thesis/blob/master/automation_tools/automated_tool_device_emulator.sh) that is similar to the :point_up: . However, it calls an [emulator script](https://github.com/amatanat/thesis/blob/master/automation_tools/send_message_emulator.sh) after extracting FS metadata. Example configuration file for the tool can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/config_2.conf.example). We have used this tool to extract XML dumps before and after implementing a user action (RM, RP, PN, PN-text) in WhatsApp in an Android device. 
The [emulator script](https://github.com/amatanat/thesis/blob/master/automation_tools/send_message_emulator.sh) is used to start an emulator, run passed python script and kill an emulator. Example configuration file for the emulator script can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/emulator.conf.example).

- Used OpenRecoveryScripts can be found [here](https://github.com/amatanat/thesis/blob/master/automation_tools/openrecoveryscript) and [here](https://github.com/amatanat/thesis/blob/master/automation_tools/openrecoveryscript2).

## [FDE XML dumps](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps)

Extracted XML dumps for the following user actions in WhatsApp in the **FDE** Android device.
- [conversation-send-message](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/conversation-send-message)
- [conversation-send-photo](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/conversation-send-photo)
- [floating-action-button send-message](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/fab-message)
- [floating-action-button send-photo](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/fab-photo)
- [receive-text-message](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/receive-message)
- [receive-photo-message](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/receive-photo)
- [push-notificaiton](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/push-notification)
- [push-notification-text](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/push-notification-text)
- [open-close](https://github.com/amatanat/thesis/tree/master/fde_xml_dumps/open-close)

[Log file](https://github.com/amatanat/thesis/blob/master/fde_xml_dumps/whatsapp.log) contains execution time of all steps in all performed actions in WhatsApp.  

## [FDE - generated tree structures](https://github.com/amatanat/thesis/tree/master/fde_generated_tree_structures)

This folder contains generated tree structures for XML dumps extracted from the **FDE** Android device.

## [FDE - diff_jsons](https://github.com/amatanat/thesis/tree/master/fde_diff_by_filename)

This folder contains reports for all selected user actions that displays which files have updated timestamp metadata after the execution of the action. [diff_json](https://github.com/amatanat/thesis/blob/master/fde_diff_by_filename/diff_jsons.py) tool generates these reports by comparing the state of each file, located inside */data/data/com.whatsapp* folder, before and after performing an action.

## [FDE - user action fingerprints](https://github.com/amatanat/thesis/tree/master/fde_action_fingerprint_generation)

- WhatsApp user action fingerprints DB can be found [here](https://github.com/amatanat/thesis/blob/master/fde_action_fingerprint_generation/fde-action-fingerprints.db)
- All [diff_json](https://github.com/amatanat/thesis/blob/master/fde_diff_by_filename/diff_jsons.py) reports are inserted into [profiles](https://github.com/amatanat/thesis/blob/master/fde_action_fingerprint_generation/action_profiles_generation.py) table in a DB.
- Changes these happened in each run of the selected actions are inserted into [fingerprints](https://github.com/amatanat/thesis/blob/master/fde_action_fingerprint_generation/action_fingerprints_generation.py) table in a DB.
- Fingerprints those are unique to each action are inserted into [characteristic-fingerprints](https://github.com/amatanat/thesis/blob/master/fde_action_fingerprint_generation/action_cfingerprints_generation.py) table in a DB.
- Fingerprints for the different action combinations are inserted into [combination-fingerprints](https://github.com/amatanat/thesis/blob/master/fde_action_fingerprint_generation/action_combination_fingerprints.py) table in a DB.

## FBE XML dumps

- Extracted [XML dumps](https://github.com/amatanat/thesis/tree/master/xml_dumps) for the selected user actions in WhatsApp in the **FBE** Android device. Corresponding WhatsApp [log file](https://github.com/amatanat/thesis/blob/master/xml_dumps/whatsapp.log).
- Extracted [XML dumps](https://github.com/amatanat/thesis/tree/master/new-fbe/fbe_xml_dumps) for the selected user actions in WhatsApp in the **FBE** Android device. Corresponding WhatsApp [log file](https://github.com/amatanat/thesis/blob/master/new-fbe/fbe-whatsapp.log). Extracted [unencrypted data](https://github.com/amatanat/thesis/tree/master/new-fbe/fbe_extracted_unencrypted_data) while generating XML dumps.

## File description in FBE

This [script](https://github.com/amatanat/thesis/blob/master/generate_tree_structures/generate_tree_structure.py) is used to describe files using counts of relatives in XML dumps.

- [File description](https://github.com/amatanat/thesis/tree/master/generate_tree_structures/tree_structure_with_encrypted_filename) for files in FBE XML dumps. It also contains encrypted filename.
- [File description](https://github.com/amatanat/thesis/tree/master/generate_tree_structures/tree_structure_without_filename) for files in FBE XML dumps.

## K-means clustering
- [clustering](https://github.com/amatanat/thesis/blob/master/clustering/clustering.py) tool creates clusters of WhatsApp DB files and extracts timestamp metadata of required files.
- [Example](https://github.com/amatanat/thesis/blob/master/clustering/k-means-clustering.png) generated clusters

## [WhatsApp user action reconstruction in FBE](https://github.com/amatanat/thesis/tree/master/wa_reconstruct_user_actions)

The folder contains used scripts for the user action reconstruction. Evaluation results can be found [here](https://github.com/amatanat/thesis/tree/master/wa_user_action_fingerprinting_evaluation). Furthermore, implemented validation test can be found [here](https://github.com/amatanat/thesis/blob/master/wa_user_action_fingerprinting_evaluation/validation-test/validation.py) and test results [here](https://github.com/amatanat/thesis/tree/master/wa_user_action_fingerprinting_evaluation/validation-test).

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

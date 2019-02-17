#!/bin/bash
#!/usr/bin/env python

source validation_config.conf

validation_script_name=$VALIDATION_SCRIPT_NAME
identified_actions_xml_path=$IDENTIFIED_ACTIONS_XML_PATH
log_file_path=$LOG_FILE_PATH
threshold=$THRESHOLD
action_name_1=$FIRST_ACTION_NAME
action_name_2=$SECOND_aCTION_NAME

counter=0
while [ $counter -le 9 ]
do
	./$validation_script_name "${identified_actions_xml_path}/${counter}/identified_user_actions.xml" "${log_file_path}/${counter}/whatsapp-actions.log" "$threshold" "$action_name_1" "$action_name_2" "$counter"
	echo $counter
	((counter++))
done
echo "All done"

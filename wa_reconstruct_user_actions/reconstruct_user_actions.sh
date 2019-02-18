#!/bin/bash
#!/usr/bin/env python

nc=$(which nc)
xnbdclient=$(which xnbd-client)

source config.conf

twrp_image_directory=$TWRP_IMAGE_DIR
twrp_image_name=$TWRP_IMAGE_NAME
nbd_server_script_directory=$NBD_SCRIPT_DIR
nbd_server_script_name=$NBD_SCRIPT_NAME
block=$BLOCK
metadata_extractor_directory=$METADATA_EXTRACTOR_DIR
metadata_extractor_filename=$METADATA_EXTRACTOR_NAME
inode=$INODE
encryption=$ENCRYPTION
whatsapp_action_script_dir=$WA_ACTION_DIR
whatsapp_action=$WA_ACTION_NAME
whatsapp_action_text=$WA_ACTION_TEXT
fs_metadata_output_file_name=$FS_METADATA_OUTPUT_NAME
matcher_script_dir=$MATCHER_SCRIPT_DIR
matcher_script_name=$MATCHER_SCRIPT_NAME
fingerprints_db_name=$FINGERPRINTS_DB_NAME
fs_metadata_output_file=$FS_METADATA_OUTPUT
xml_extracted_fingerprints_dir=$XML_EXTRACTED_FING_DIR
xml_extracted_fingerprints_name=$XML_EXTRACTED_FING_NAME
matcher_output_file_name=$MATCHER_OUTPUT_NAME
matcher_output_file=$MATCHER_OUTPUT
linking_tool_dir=$LINKED_TOOL_DIR
link_folders=$LINKED_TOOL_NAME
linked_folders_file_dir=$LINKED_FOLDERS_FILE_DIR
linked_folders_file_name=$LINKED_FOLDERS_FILE_NAME
linked_folders=$LINKED_FOLDERS
clustering_dir=$CLUSTERING_DIR
identify_WA_folder_inode=$IDENTIFY_WA_FOLDER_INODE_SCRIPT
identified_WA_inode=$IDENTIFIED_WA_FOLDER_INODE_NAME
clustering_script_name=$CLUSTERING_SCRIPT_NAME
clustering_output_file_name=$CLUSTERING_OUTPUT_NAME
identify_user_action_script_name=$IDENTIFY_USER_ACTION_SCRIPT
threshold=$THRESHOLD
identified_user_actions=$IDENTIFIED_USER_ACTION_NAME
WA_inode_filename=$WA_INODE_FILENAME
emulator_script_path=$EMULATOR_SCRIPT


boot_twrp () {
	adb reboot bootloader
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1s; done
	echo "fastboot device is available.."
	cd $twrp_image_directory
	fastboot boot $1 
}

kill_process () {
	PID=`ps -eaf | grep $1 | grep -v grep | awk '{print $2}'`
	if [[ "" !=  "$PID" ]]; then
  		echo "killing $PID"
  		kill -9 $PID
	fi
}

check_file_existence () {
	while true
	do
	  if [ -f $1 ] ; then
    	  	echo "file exists.."
		break
	  fi
	done
}

wait_device_screen () {
	adb wait-for-device
	while true
	do 
	  if [ "$(adb shell dumpsys nfc | grep 'mScreenState=')" == "mScreenState=ON_UNLOCKED" ]; then 
		break
	  fi
	done
	echo "device screen is ON..."
}

extract_fs_metadata () {
	echo "extracting FS metadata.."
	boot_twrp "$twrp_image_name"
	until [ $(adb devices | sed -n '2p' | grep -c 'recovery') != 0 ]; do 
		sleep 1s	
	done
	
	echo "adb device is available.."

	cd $nbd_server_script_directory
	adb push $nbd_server_script_name /tmp/nbdserver.sh
	sleep 15s
	echo "adb push is done..."	

	adb shell "
		cd /tmp/
		chmod +x nbdserver.sh
		./nbdserver.sh $block 8992 " &
	# must sleep before the next command
	sleep 5s

	adb forward tcp:8992 tcp:8992 
	until [ $(netstat -plnt | grep -c 8992) == 1 ]; do sleep 1s; done

	$xnbdclient bs=4096 127.0.0.1 8992 /dev/nbd0 &

	cd $metadata_extractor_directory
	python $metadata_extractor_filename /dev/nbd0 $inode $1 $encryption &

	# wait until previous command ends, i.e metadata extraction 
	# if an xml file exists then the extraction process is finished
	check_file_existence "$1.xml"
}



#source "$emulator_script_path" &
#wait

# implement WhatsApp action
cd $whatsapp_action_script_dir
./$whatsapp_action
# wait 10 seconds before performing second WA action
sleep 10
./$whatsapp_action_text
echo "whatsapp_action end.."

sleep 10

# extract FS metadata to an XML file
extract_fs_metadata "$fs_metadata_output_file_name"
echo "extract_fs_metadata end.."

cd $matcher_script_dir
./$matcher_script_name "$fingerprints_db_name" "$fs_metadata_output_file" "$xml_extracted_fingerprints_dir" "$xml_extracted_fingerprints_name" "$matcher_output_file_name"
echo "matcher script  end.."

cd $linking_tool_dir
./$link_folders "$fs_metadata_output_file" "$linked_folders_file_dir" "$linked_folders_file_name"
echo "linking tool end.."

cd $clustering_dir
./"$identify_WA_folder_inode" "$matcher_output_file" "$linked_folders" "$identified_WA_inode"
./$clustering_script_name "$fs_metadata_output_file" "$WA_inode_filename" "$clustering_output_file_name" 
echo "clustering end.."

./$identify_user_action_script_name "$clustering_output_file_name.json" "$threshold" "$identified_user_actions"
echo "identify user action end.."

# reboot system
adb shell "reboot system"
# wait until device screen is ON
wait_device_screen
echo "Done"



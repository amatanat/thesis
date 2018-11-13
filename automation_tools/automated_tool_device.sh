#!/bin/bash
#!/usr/bin/env python
# Author:       Matanat Ahmadova
# Description:	Full automated tool for the Android device to perform app actions and extract FS metadata. 
# 
#
#

nc=$(which nc)
xnbdclient=$(which xnbd-client)
device_turned_on=false

source config.conf

runCount=$RUN_COUNT 
twrp_image_directory=$TWRP_DIR
twrp_image_name=$TWRP_IMAGE_NAME
nbd_server_script_directory=$NBD_SERVER_SCRIPT_DIR
nbd_server_script_name=$NBD_SERVER_SCRIPT_NAME
metadata_extractor_directory=$FBE_FIWALK_DIR
metadata_extractor_filename=$FBE_FIWALK_NAME
inode=$INODE_NUMBER
xml_output_name_1=$OUTPUT_XML_DUMP_BEFORE
xml_output_name_2=$OUTPUT_XML_DUMP_AFTER
python_script_directory=$APP_AUTOMATION_SCRIPT_DIR
python_script_name=$APP_AUTOMATION_SCRIPT_NAME

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
		if [ $(adb devices | sed -n '2p' | grep -c 'device') == 1 ]; then
			$device_turned_on=true
			break
		fi	
	done
	if [ "$device_turned_on" = true ] ; then
		break
	fi
	echo "adb device is available.."

	cd $nbd_server_script_directory
	adb push $nbd_server_script_name /tmp/nbdserver.sh
	sleep 10s
	echo "adb push is done..."	

	adb shell "
		cd /tmp/
		chmod +x nbdserver.sh
		./nbdserver.sh /dev/block/mmcblk0p45 8992 " &
	# must sleep before the next command
	sleep 5s

	adb forward tcp:8992 tcp:8992 
	until [ $(netstat -plnt | grep -c 8992) == 1 ]; do sleep 1s; done

	$xnbdclient bs=4096 127.0.0.1 8992 /dev/nbd0 &

	cd $metadata_extractor_directory
	python $metadata_extractor_filename /dev/nbd0 $inode $1 FBE &

	# wait until previous command ends, i.e metadata extraction 
	# if an xml file exists then the extraction process is finished
	check_file_existence "$1.xml"
}


# copy openrecoveryscript 
adb shell "
 su -c 'cp /sdcard/Download/openrecoveryscript /cache/recovery/.
 ls /cache/recovery/'"

# create a backup
boot_twrp "$twrp_image_name"
echo "creating a backup.."

wait_device_screen

counter=1
while [ $counter -le $runCount ]
do
	kill_process "adb" & 
	wait
	kill_process "xnbd-client" &
	wait

	# extract FS metadata to an XML file
	metadata_before_action=${xml_output_name_1}_${counter}
	extract_fs_metadata "$metadata_before_action"
	echo "extract_fs_metadata end: before an app action.."
	if [ "$device_turned_on" = true ] ; then
		$device_turned_on=false
		continue
	fi

	# reboot system
	adb shell "reboot system"
	
	wait_device_screen

	# run python script
	cd $python_script_directory
	./$python_script_name
	echo "python script end.."
	
	# extract FS metadata to an XML file after an app action 
	metadata_after_action=${xml_output_name_2}_${counter}
	extract_fs_metadata "$metadata_after_action"
	echo "extract_fs_metadata end: after an app action.."
	if [ "$device_turned_on" = true ] ; then
		$device_turned_on=false
		continue
	fi

	# reboot system
	adb shell "reboot system"
	
	wait_device_screen 

	# copy openrecoveryscript 
	adb shell "
	 su -c 'cp /sdcard/Download/openrecoveryscript2 /cache/recovery/openrecoveryscript
	 ls /cache/recovery/
	 '"
	
	# restore the backup
	boot_twrp "$twrp_image_name"
	echo "restoring a backup.."
	
	wait_device_screen	

	echo $counter
	((counter++))
done
echo "All done"


#!/bin/bash
#!/usr/bin/env python
# Author:       Matanat Ahmadova
# Description:	Full automated tool for the Android device to perform app actions and extract FS structure and metadata. 
# 
#
#

nc=$(which nc)
xnbdclient=$(which xnbd-client)

echo "Number of runs:" 
read runCount
echo "Name of the XML output before the application run: "
read xml_output_name_1
echo "Name of the XML output after the application run: "
read xml_output_name_2
echo "Directory of the twrp image: " 
read twrp_image_directory
echo "twrp image name for the backup creation: "
read twrp_image_for_backup
echo "twrp image name for the NBD use: "
read twrp_image_for_nbd
echo "Directory of the NBD server script: "
read nbd_server_script_directory
echo "Name of the NBD server script: "
read nbd_server_script_name
echo "FS metadata extractor directory: "
read extractor_directory
echo "FS metadata extractor name: "
read extractor_filename
echo "inode number: "
read inode
echo "Directory of the python script for the app automation: " 
read python_script_directory
echo "Name of the python script for the app automation: "
read python_script_name

boot_twrp () {
	adb reboot bootloader
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1s; done
	echo "fastboot device is available.."
	cd $twrp_image_directory
	fastboot boot $1 
}

extract_fs_metadata () {
	echo "Extracting FS metadata.."
	boot_twrp "$twrp_image_for_nbd"
	until [ $(adb devices | sed -n '2p' | grep -c 'recovery') != 0 ]; do sleep 1s; done
	echo "adb device is available.."
	cd $nbd_server_script_directory
	# TODO  check 
	adb push $nbd_server_script_name /tmp/nbdserver.sh
	adb shell "
	cd /tmp/
	chmod +x nbdserver.sh
	./nbdserver.sh /dev/block/mmcblk0p45 8992 " &
	# TODO check sleep
	sleep 10s
	adb forward tcp:8992 tcp:8992
	until [ $(netstat -plnt | grep -c 8992) == 1 ]; do sleep 1s; done
	$xnbdclient bs=4096 127.0.0.1 8992 /dev/nbd0
	cd $extractor_directory
	python $extractor_filename /dev/nbd0 $inode $1 FBE &
	wait
}

wait_device () {
	#until [ $(adb devices | sed -n '2p' | grep -c 'device') != 0 ]; do sleep 1s; done
	while true
	 do 
	   if [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" == "1" ]; then 
		break
           fi 
        done
	echo "device is available.."
}

# copy openrecoveryscript 
adb shell "
 su -c 'cp /sdcard/Download/openrecoveryscript /cache/recovery/.
 ls /cache/recovery/'"

# create a backup
boot_twrp "$twrp_image_for_backup"
echo "Creating a backup.."

wait_device

counter=1
while [ $counter -le $runCount ]
do
	# extract FS metadata to an XML file
	metadata_before_action=${xml_output_name_1}_${counter}
	extract_fs_metadata "$metadata_before_action"
	echo "extract_fs_metadata end: before an app action.."

	# reboot system
	adb shell "reboot system"
	
	wait_device

	# run python script
	cd $python_script_directory
	./$python_script_name
	echo "python script end.."
	
	# extract FS metadata to an XML file after an app action 
	metadata_after_action=${xml_output_name_2}_${counter}
	extract_fs_metadata "$metadata_after_action"
	echo "extract_fs_metadata end: after an app action.."

	# copy openrecoveryscript 
	adb shell "
	 cp /sdcard/Download/openrecoveryscript2 /cache/recovery/openrecoveryscript
	 ls /cache/recovery/
	 reboot bootloader"
	
	# restore the backup
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1; done
	cd $twrp_image_directory
	fastboot boot $twrp_image_for_backup
	echo "Restoring a backup.."
	
	wait_device	

	echo $counter
	((counter++))
done
echo "All done"

#!/bin/bash
#!/usr/bin/env python
# Author:       Matanat Ahmadova
# Description:	Full automated tool for the Android device to perform app actions and generate FS dumps. 
# 
#
#

nc=$(which nc)

echo "Number of FS dumps:" 
read fsDumpCount
echo "Name of the FS dump after the application run: "
read filename_fs
echo "Name of the FS dump before the application run: "
read restored_filename_fs
echo "Directory of the twrp image: " 
read twrp_image_directory
echo "Directory of the python script for the app automation: " 
read python_script_directory
echo "Name of the python script for the app automation: "
read python_script_name

boot_twrp () {
	adb reboot bootloader
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1s; done
	echo "fastboot device is available.."
	cd $twrp_image_directory
	fastboot boot twrp-3.2.1-0-bullhead.img 
}

dump_FS () {
	echo "Creating FS dump.."
	boot_twrp
	until [ $(adb devices | sed -n '2p' | grep -c 'recovery') != 0 ]; do sleep 1s; done
	echo "adb device is available.."
	adb forward tcp:8992 tcp:8992
	until [ $(netstat -plnt | grep -c 8992) == 1 ]; do sleep 1s; done
	adb shell "nc -l -p 8992 < /dev/block/mmcblk0p45" & 
	sleep 10s
	$nc localhost 8992 > $1 & 
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
boot_twrp 
echo "Creating a backup.."

wait_device

counter=1
while [ $counter -le $fsDumpCount ]
do
	# create FS dump
	userdata_before_action=${restored_filename_fs}_${counter}
	dump_FS "$userdata_before_action.img"
	echo "FS dump end: before an app action.."

	# reboot system
	adb shell "reboot system"
	
	wait_device

	# run python script
	cd $python_script_directory
	./$python_script_name
	echo "python script end.."
	
	# create FS dump
	userdata_after_action=${filename_fs}_${counter}
	dump_FS "$userdata_after_action.img"
	echo "FS dump end: after an app action.."

	# copy openrecoveryscript 
	adb shell "
	 cp /sdcard/Download/openrecoveryscript2 /cache/recovery/openrecoveryscript
	 ls /cache/recovery/
	 reboot bootloader"
	
	# restore the backup
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1; done
	cd $twrp_image_directory
	fastboot boot twrp-3.2.1-0-bullhead.img
	echo "Restoring a backup.."
	
	wait_device	

	echo $counter
	((counter++))
done
echo "All done"

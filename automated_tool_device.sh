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
echo "Name of the FS dump of restored backup: "
read restored_filename_fs
echo "Directory of the twrp image: " 
read twrp_image_directory
echo "Directory of the python script for the app automation: " 
read python_script_directory
echo "Name of the python script for the app automation: "
read python_script_name

boot_twrp () {
	adb reboot bootloader
	sleep 10s
	cd $twrp_image_directory
	fastboot boot twrp-3.2.1-0-bullhead.img
}

dump_FS () {
	echo "Creating FS dump"
	boot_twrp
	sleep 15s
	adb forward tcp:8992 tcp:8992
	sleep 5s
	adb shell "nc -l -p 8992 < /dev/block/mmcblk0p45" & 
	sleep 10s
	$nc localhost 8992 > $1 & 
	wait	
}

# copy openrecoveryscript 
adb shell "
 su -c 'cp /sdcard/Download/openrecoveryscript /cache/recovery/.
 ls /cache/recovery/'"

# create a backup
boot_twrp 
echo "Creating a backup.."
sleep 3m


counter=1
while [ $counter -le $fsDumpCount ]
do
	# run python script
	cd $python_script_directory
	./$python_script_name
	echo "python script end"
	
	# create FS dump
	userdata=${filename_fs}_${counter}
	dump_FS "$userdata.img"
	echo "FS dump end"

	# copy openrecoveryscript 
	adb shell "
	 cp /sdcard/Download/openrecoveryscript2 /cache/recovery/openrecoveryscript
	 ls /cache/recovery/
	 reboot bootloader"
	
	# restore the backup
	sleep 15s
	cd $twrp_image_directory
	fastboot boot twrp-3.2.1-0-bullhead.img
	echo "Restoring a backup.."
	sleep 8m

	# create FS dump
	userdata_after_restore=${restored_filename_fs}_${counter}
	dump_FS "$userdata_after_restore.img"
	echo "FS dump end: backup restore "
	
	# reboot system
	adb reboot system
	sleep 1m

	echo $counter
	((counter++))
done
echo "All done"

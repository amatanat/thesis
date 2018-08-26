#!/bin/bash
#!/usr/bin/env python
# Author:       Matanat Ahmadova

# start the emulator, install and register an application, save a snapshot.
# emulator configuration: 
	# graphics: Hardware
	# Boot option: Cold boot
	# RAM: 2048 MB
	# Internal storage: 1024 MB
	# SD card: 1024 MB
	# Extended controls > snapshots > Settings >  Save quick-boot state on exit - NO

echo "Number of FS dumps:"
read fsDumpCount
echo "Directory of the python script for the app automation: " 
read python_script_directory
echo "Name of the python script for the app automation: "
read python_script_name
echo "Directory of the emulator: " 
read emulator_directory
echo "Name of the emulator: "
read emulator_name
echo "Name of the emulator snapshot: "
read emulator_snapshot_name
echo "Directory of the avd image files: "
read avd_image_directory

counter=1
while [ $counter -le $fsDumpCount ]
do
	# run python script
	cd $python_script_directory
	./$python_script_name
	echo "python script end"

	# copy required img files
	qemu_image=userdata-qemu_${counter}.img
	qcow_image=userdata-qemu_${counter}.img.qcow2
	cd $avd_image_directory
	cp userdata-qemu.img.qcow2 $avd_image_directory/tmp/$qcow_image
	cp userdata-qemu.img $avd_image_directory/tmp/$qemu_image
	echo "copy is done"	

	# use the script to kill an emulator
	expect -c "
	
	set timeout 10

	# Start telnet session
	spawn telnet localhost 5554
	expect \"OK\"
	send \"kill\r\"
	expect \"bye\"
	"
	
	sleep 10s
	# start the emulator snapshot
	echo "emulator snapshot starting.."
	cd $emulator_directory
	./emulator -avd $emulator_name -snapshot $emulator_snapshot_name &
	sleep 1m

	echo $counter
	((counter++))
done
echo "All done"


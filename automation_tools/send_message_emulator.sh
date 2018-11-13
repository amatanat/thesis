#!/bin/bash
#!/usr/bin/env python

kill_emulator () {
# use the script to kill an emulator
	expect -c "
	
		set timeout 10
	
		# Start telnet session
		spawn telnet localhost 5554
		expect \"OK\"
		send \"kill\r\"
		expect \"bye\"
	"
}

source emulator.conf

python_script_directory=$APP_AUTOMATION_SCRIPT_DIR
python_script_name=$APP_AUTOMATION_SCRIPT_NAME
android_sdk_emulator_dir=$EMULATOR_DIR
avd_name=$AVD_NAME

cd $android_sdk_emulator_dir
./emulator -avd $avd_name &
while [ $(adb devices | grep -c 'device') != 3 ] ; do sleep 1; done

emulator_serialno=$(adb devices| grep emulator| cut -f1)
echo $emulator_serialno
sleep 5s

adb start-server
sleep 5s

# run python script
cd $python_script_directory
./$python_script_name $emulator_serialno
echo "emulator python script end"
sleep 5s

kill_emulator


	

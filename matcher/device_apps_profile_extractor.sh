#!/bin/bash

extract_apps_profile () {
	echo "name-"$1 >> "file.txt"
	R=$(adb shell "
		su -c ' cd /data/app/
			cd \$(ls -d * | grep \"$1\")
			find * |xargs stat -c \"%s %n\" '")
	echo "$R" >> "file.txt"
}

for app_name in $(adb shell "
 		su -c 'cmd package list packages -3 | cut -f 2 -d \":\" '"); do

	app_name=${app_name%$'\r'}		
	extract_apps_profile "$app_name" 
	
done




#!/bin/bash

extract_app_fingerprints () {
	echo "name-"$1 >> $4
	echo $2 >> $4
	echo $3 >> $4
	R=$(adb shell "
		su -c ' cd /data/app/
			cd \$(ls -d * | grep \"$1-\")
			find * -type f | egrep -v '^oat' |xargs stat -c \"%s %n\" '") 
	echo "$R" >> $4
}

for app_name in $(adb shell "
 		su -c 'cmd package list packages -3 | cut -f 2 -d \":\" '"); do

	app_name=${app_name%$'\r'}
	version_name=$(adb shell "
		su -c 'dumpsys package \"$app_name\" | grep -i versionName'")
	version_code=$(adb shell "
		su -c 'dumpsys package \"$app_name\" | grep -i versionCode'")
	extract_app_fingerprints "$app_name" "$version_name" "$version_code" "$1"
	
done




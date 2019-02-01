#!/bin/bash
#!/usr/bin/env python

source evaluation_config.conf

copy_apks_script_path=$COPY_APKS_SCRIPT_PATH
apk_files_location=$APK_FILES_LOCATION
fing_generation_app_dir=$FINGERPRINT_GENERATION_APP_DIR
fing_generation_app_name=$FINGERPRINT_GENERATION_APP_NAME
app_fingerprints_db_name=$APP_FINGERPRINTS_DB_NAME
device_app_fingerprints_file_dir=$DEVICE_APP_FINGERPRINTS_DIR
device_app_fingerprints_filename=$DEVICE_APP_FINGERPRINTS_NAME
matcher_script_path=$MATCHER_SCRIPT_PATH
inode_output_filename=$APP_INODES_OUTPUT_NAME
count_matches_script_name=$COUNT_MATCHES_SCRIPT_NAME
count_result_output_dir=$COUNT_RESULT_OUTPUT_DIR
count_result_output_filename=$COUNT_RESULT_OUTPUT_FILENAME
matcher_report_dir=$MATCHER_REPORT_DIR
matcher_report=$MATCHER_REPORT_NAME
runCount=$RUN_COUNT


list_app_inodes	() {
	R=$(adb shell "
	 	su -c ' 
		       cd /data/app/
		       ls -i '")
	echo $R >> $1

}

uninstall_apps () {
	for x in $(adb shell "
	    		    su -c '
				pm list packages -3 | cut -f 2 -d \":\" | grep -v "^eu.chainfire.supersu" '"); do adb uninstall ${x%$'\r'};  done
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

counter=11
while [ $counter -le $runCount ]
do
	"$copy_apks_script_path"
	echo "50 apk files are copied"

	# install all apps in given directory
	cd $apk_files_location
	ls -1 *.apk | xargs -l adb install
	echo "installed apps to a device.."

	# extract fingerprints for installed applications
	cd $fing_generation_app_dir
	./$fing_generation_app_name "$app_fingerprints_db_name" "${device_app_fingerprints_file_dir}${counter}" "${device_app_fingerprints_filename}_${counter}"
	echo "fingerprint generation end.."

	"$matcher_script_path" "$counter"
	echo "matcher script end.."

	adb shell "reboot system"

	wait_device_screen

	list_app_inodes "${device_app_fingerprints_file_dir}${counter}/${inode_output_filename}_${counter}"
	echo "apps inode extraction end.."

	uninstall_apps
	echo "uninstall apps from a device end.."

	cd $count_result_output_dir
	./$count_matches_script_name "${matcher_report_dir}${counter}" "${matcher_report}_${counter}.json" "$count_result_output_dir" "${count_result_output_filename}"
	echo "count_matches end.."

	# remove all apks in given directory
	rm $apk_files_location/*
	echo "remove files from /apks dir. end.."

	echo $counter
	((counter++))
done
echo "All done.."


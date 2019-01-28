#!/bin/bash
#!/usr/bin/env python

nc=$(which nc)
xnbdclient=$(which xnbd-client)
device_turned_on=false

source config.conf

twrp_image_directory=$TWRP_DIR
twrp_image_name=$TWRP_IMAGE_NAME
nbd_server_script_directory=$NBD_SERVER_SCRIPT_DIR
nbd_server_script_name=$NBD_SERVER_SCRIPT_NAME
metadata_extractor_directory=$FBE_EXTRACTOR_DIR
metadata_extractor_filename=$FBE_EXTRACTOR_NAME
inode=$INODE_NUMBER
encryption=$ENCRYPTION_NAME
block=$BLOCK
xml_output_name=$OUTPUT_XML_DUMP
matcher_directory=$MATCHER_SCRIPT_DIR
matcher_script_name=$MATCHER_SCRIPT_NAME
matcher_output_name=$MATCHER_OUTPUT_NAME
app_fingerprints_db_dir=$APP_FING_DB_DIR
app_fingerprints_db_name=$APP_FING_DB_NAME
matcher_xml_extracted_fing_name=$MATCHER_XML_EXTRACTED_FING_NAME


boot_twrp () {
	adb reboot bootloader
	until [ $(fastboot devices | grep -c 'fastboot') != 0 ]; do sleep 1s; done
	echo "fastboot device is available.."
	cd $twrp_image_directory
	fastboot boot $1 
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


# extract FS metadata to an XML file
extract_fs_metadata "$xml_output_name" 
echo "extract_fs_metadata end.."

cd $matcher_directory
./$matcher_script_name "$app_fingerprints_db_dir/$app_fingerprints_db_name" "$xml_output_name.xml" "$matcher_xml_extracted_fing_name" "$matcher_output_name"
echo "python script end.."





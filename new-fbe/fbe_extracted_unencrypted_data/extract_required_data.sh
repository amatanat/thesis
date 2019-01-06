#!/bin/bash
#!/usr/bin/env python

extract_app_data () {
		
	R=$(adb -d shell "
		su -c ' cd /data/data/
			stat \"$1\"'")
	echo "$R" >> "$2.txt"
	
}

find_files () {
	K=$(adb -d shell "
		su -c ' cd /data/data/com.whatsapp/
			find * -type f '")
	echo "$K" >> "$1.txt"

}

list_folder () {
	F=$(adb -d shell "
		su -c ' cd /data/data/com.whatsapp/
			ls -lR '")
	echo "$F" >> "$1.txt"

}


extract_app_data "com.whatsapp/" "$1" 
find_files "$1" 
list_folder "$1" 

#!/bin/bash

a=0
b=60

source "copy_apks_config.conf"

for i in `ls $file_dir`; do  
	for file in `ls $file_dir/$i`; do 
		if [ ${file: -4} == ".apk" ] && [ ${file:0:18} != "com.google.android" ]; then
			if [ "$file" == "`grep $file evaluated_apks.txt`" ]; then
				echo "$file is evaluated"
			else 
				if [ $a -lt $b ]; then		
					echo "$file is not evaluated"
					beginning=${file%_*}
					if [ `grep "$beginning" copied_apks.txt` ]; then
						echo "$file another version is available in txt file"
					else
						echo "$file version is not available in txt file"
						echo $file >> evaluated_apks.txt
						echo $file >> copied_apks.txt
						echo "$file_dir$i/$file"
						cp "$file_dir$i/$file" "$directory_to_copy"
						((a+=1))
					fi;
				else
					echo "count is 60"
					echo " " > copied_apks.txt
					break 2
				fi;
			fi;
		fi; 
	done;
done;


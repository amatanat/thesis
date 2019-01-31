#! /usr/bin/env python

import sys
import json
import os.path

def output_result(result):
	with open(os.path.expanduser(os.path.join(output_file_dir, output_filename + ".txt")), 'a') as f:
     		f.write(json.dumps(result) + '\n')

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python count_found_matches.py <json_dir> <json_filename> <output_file_dir> <output_filename>"
		exit()

	input_file_dir =  sys.argv[1]
	input_filename = sys.argv[2] 
	output_file_dir = sys.argv[3]
	output_filename =  sys.argv[4]
	
	output = {}
	
	identified = 0
	unidentified = 0
	multiple_apps_identified = 0
	with open(os.path.join(input_file_dir, input_filename), "r") as f:
  			found_matches = json.loads(f.read())
			for inode, app_name in found_matches.items():
				if app_name == "unknown":
					unidentified += 1
				else:
					for item in app_name:
						if isinstance(item, unicode):
							identified += 1	
						else:
							multiple_apps_identified += 1		

			output["unidentified"] = unidentified
			output["identified"] =  identified/2
			output["multiple_apps_identified"] = multiple_apps_identified/2	

			output_result(output)		


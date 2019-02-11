#! /usr/bin/env python

import sys
import json
import os.path

def output_result(result):
	with open(os.path.expanduser(os.path.join(output_file_dir, output_filename + ".txt")), 'w+') as f:
     		f.write(json.dumps(result) + '\n')

def count_found_matches (found_matches):
	identified = 0
	unidentified = 0
	different_apps_identified = 0
	for inode, app_data in found_matches.items():
		if app_data == "unknown":
			unidentified += 1
		else:
			if isinstance(app_data[0], unicode):
				identified += 1	
			else:
				different_apps_identified += 1

	output["unidentified apps count"] = unidentified
	output["identified apps count"] =  identified
	output["different apps identified"] = different_apps_identified

def extract_inode_app_name(matcher_result):
	matched_apps_dict = dict()
	for key, value in matcher_result.items():
		if value == "unknown":
			matched_apps_dict[key] = value
		elif len(value) == 3:
			matched_apps_dict[key] = value[0]
		else:
			for i in value:
				if key in matched_apps_dict:
					if not matched_apps_dict[key] == i[0]:
						matched_apps_dict[key] = (matched_apps_dict[key], i[0])
				else:
					matched_apps_dict[key] = i[0]
	return matched_apps_dict

def extract_device_inode_app_name (device_app_inodes):
	app_inodes_dict = dict()
	for line in device_app_inodes:
		line = line.split('-')[0].lstrip().rstrip().split(" ")
		key = line[0]
		value = line[1]
		app_inodes_dict[key] = value
	return app_inodes_dict

def verify_matched_inodes (device_data, matcher_result):
	output["correct identified inode-app_name"] = list()
	output["unidentified inode-app_name"] = list()
	output["wrong identified inode-app_name"] = list()

	for key, value in matcher_result.items():
		if matcher_result[key] == device_data[key]:
			output["correct identified inode-app_name"].append((key, value))

		elif matcher_result[key] != device_data[key] and matcher_result[key] == "unknown":
			output["unidentified inode-app_name"].append((key, value, device_data[key]))

		else:
			output["wrong identified inode-app_name"].append((key, value, device_data[key]))


if __name__ == '__main__':
	if len(sys.argv) < 6:
		print "Usage: python evaluate_matcher_result.py <matcher_result_json_dir> <matcher_result_json_filename> <device_app_inodes_txt> <output_file_dir> <output_filename>"
		exit()

	input_file_dir =  sys.argv[1]
	input_filename = sys.argv[2] 
	device_app_inodes_txt = sys.argv[3]
	output_file_dir = sys.argv[4]
	output_filename =  sys.argv[5]
	
	output = dict()

	with open(device_app_inodes_txt) as f:
    		device_app_inodes = f.read().splitlines()
		device_data = extract_device_inode_app_name(device_app_inodes)

	with open(os.path.join(input_file_dir, input_filename), "r") as f:
  		found_matches = json.loads(f.read())
		count_found_matches(found_matches)
		matcher_result = extract_inode_app_name(found_matches)
	
	verify_matched_inodes(device_data, matcher_result)
	output_result(output)		


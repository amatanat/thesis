#!/usr/bin/env python
import sys
import json

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python identify_WA_folder_inode.py <matcher_result> <linked_tool_result> <output_filename>"
		exit()

	matcher_result = sys.argv[1]
	linked_tool_result = sys.argv[2]
	output_filename = sys.argv[3]

	with open(matcher_result, "r") as f:
  		matcher_data = json.loads(f.read())

	with open(linked_tool_result, "r") as f:
  		linked_tool_data = json.loads(f.read())

	for key, value in matcher_data.items():
		if len(value) == 3 and value[0] == "com.whatsapp":
			wa_app_folder_inode = key
			break

	for key, value in linked_tool_data.items():
		if key == "/data/app/->/data/data/":
			for  app_folder_inode, data_folder_inode in value.items():
				if app_folder_inode == wa_app_folder_inode:
					wa_inode = data_folder_inode
					break

	with open(output_filename + ".json", 'w+') as f:
     		f.write(json.dumps(wa_inode))

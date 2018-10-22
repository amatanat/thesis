#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import collections
import json

files_size_dict = {}

def get_app_folder_inode ():
	return root.find("./fileobject/[filename='app']").find('inode').text

def create_dict (inode):
	files_size_dict[inode] = list()
	find_files_size(inode, inode)

def find_app_subfolders (inode):
	for fileobject in e.findall('fileobject'):
		parent_inode = fileobject.find('parent_object').find('inode').text
		name_type = fileobject.find('name_type').text 
		i_node = fileobject.find('inode').text
		if (parent_inode is not None and int(parent_inode) == int(inode) and 
			str(name_type) == str("d/d")):

			create_dict(int(i_node))

def find_files_size (inode, root_folder_inode):
	for fileobject in e.findall('fileobject'):
		parent_inode = fileobject.find('parent_object').find('inode').text
		name_type = fileobject.find('name_type').text 
		filesize = fileobject.find('filesize').text 
		i_node = fileobject.find('inode').text
		if (parent_inode is not None and int(parent_inode) == int(inode) and 
			str(name_type) == str("d/d") and filesize is not None):
			

			find_files_size(i_node, root_folder_inode)

		elif (parent_inode is not None and int(parent_inode) == int(inode) and
			str(name_type) == "r/r" and filesize is not None):

			files_size_dict[root_folder_inode].append([int(i_node), int(filesize)])

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "Usage: python xml_files_size_extractor.py <xml_dump_name> <output_filename>"
		exit()

	xml_dump = sys.argv[1] 
	output = sys.argv[2] + ".txt"
	root = ET.parse(xml_dump).getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	e = ET.fromstring(xmlstr)

	inode = get_app_folder_inode()
	find_app_subfolders(inode)
	with open(output, 'w+') as f:
     		f.write(json.dumps(files_size_dict))



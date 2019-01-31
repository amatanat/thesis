#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import collections
import json
import os.path


fingerprints = {}
check_oat = False

def get_app_folder_inode ():
	return root.find("./fileobject/[filename='app']").find('inode').text

def create_dict (inode):
	global check_oat
	check_oat = False

	fingerprints[inode] = list()
	find_fingerprints(inode, inode, 'root')

def find_app_subfolders (inode):
	for fileobject in e.findall('fileobject'):
		parent_inode = fileobject.find('parent_object').find('i_node').text
		name_type = fileobject.find('name_type').text 
		i_node = fileobject.find('inode').text
		if (parent_inode is not None and int(parent_inode) == int(inode) and 
			str(name_type) == str("d/d")):

			create_dict(int(i_node))

def find_children_count (inode):
	""" Return children files' count in a given folder """
	count = 0
	for fileobject in e.findall('fileobject'):
		parent_inode = fileobject.find('parent_object').find('i_node').text
		name_type = fileobject.find('name_type').text 
		if (parent_inode is not None and int(parent_inode) == int(inode) and 
			str(name_type) == str("r/r")):
			count += 1
	return count

def find_type (count):
	if not count in (2,3):
		return 'lib'
	else:	
		global check_oat
		if not check_oat:
			check_oat = True
			return 'oat'
		else:
			return 'unknown'
		

def find_fingerprints (inode, root_folder_inode, file_type):
	for fileobject in e.findall('fileobject'):
		parent_inode = fileobject.find('parent_object').find('i_node').text
		name_type = fileobject.find('name_type').text 
		filesize = fileobject.find('filesize').text 
		i_node = fileobject.find('inode').text

		if (parent_inode is not None and int(parent_inode) == int(inode) and 
			str(name_type) == str("d/d") and filesize is not None):
			
			file_type = find_type(find_children_count(i_node))
			find_fingerprints(i_node, root_folder_inode, file_type)

		elif (parent_inode is not None and int(parent_inode) == int(inode) and
			str(name_type) == "r/r" and filesize is not None):
			
			if (int(parent_inode) == root_folder_inode):
				file_type = 'root'

			fingerprints[root_folder_inode].append([int(i_node), int(filesize), file_type])


if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Usage: python xml_fingerprints_extractor.py <xml_dump_name> <output_filename> <output_file_dir>"
		exit()

	xml_dump = sys.argv[1] 
	output = sys.argv[2] 
	output_dir = sys.argv[3]
	root = ET.parse(xml_dump).getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	e = ET.fromstring(xmlstr)

	inode = get_app_folder_inode()
	find_app_subfolders(inode)
	with open(os.path.expanduser(os.path.join(output_dir, output + ".txt")), 'w+') as f:
     		f.write(json.dumps(fingerprints))



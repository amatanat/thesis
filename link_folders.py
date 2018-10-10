#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import collections

def get_app_folder_inode ():
	return root.find("./fileobject/[filename='app']").find('inode').text

def get_data_folder_inode ():
	return root.find("./fileobject/[filename='data']").find('inode').text		

def get_genId_crdate_dict (inode):
	"""Given root folder's inode number
	Find children folders and return a dictionary containing 
	generation id and creation date of found folders"""
	genId_crdate_dict = {}
	for fileobject in e.findall('fileobject'):
		# get parent's inode value
		parent_inode = fileobject.find('parent_object').find('inode').text
		name_type = fileobject.find('name_type').text 
		if (parent_inode is not None and int(parent_inode) == int(inode) and str(name_type) == "d/d"):
			# get folder's creation date
			crdate = str(fileobject.find('crtime').text).split("T")
			genId_crdate_dict[int(fileobject.find('genId').text)] = crdate[0]
	# sort a dictionary by key
	return collections.OrderedDict(sorted(genId_crdate_dict.items()))

def link_folders(app_genId_crdate_dict, data_genId_crdate_dict):
	"""Given generation id-creation date dictionary
	of apps in data/app and data/data folders.
	Link apps' data/app folder to data/data folder
	return a generation id dictionary containing genIds of linked folders,
	genIdAppFolder: genIdDataFolder"""
	linked_genIds = {}
	for key_a, value_a in app_genId_crdate_dict.items():
		link_prev, link_next, key = app_genId_crdate_dict._OrderedDict__map[key_a] 
		for key_d, value_d in data_genId_crdate_dict.items():
			if key_d > key_a and key_d < link_next[2] and value_a == value_d:
				linked_genIds[key_a] = key_d
	return linked_genIds

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: python link_folders.py <xml_dump_name>"
		exit()

	xml_dump = sys.argv[1] 
	root = ET.parse(xml_dump).getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	e = ET.fromstring(xmlstr)
	
	app_folder_inode = get_app_folder_inode()
	app_genId_crdate_dict = get_genId_crdate_dict(app_folder_inode)

	data_folder_inode = get_data_folder_inode()
	data_genId_crdate_dict = get_genId_crdate_dict(data_folder_inode)

	linked_folders_genId = link_folders(app_genId_crdate_dict,data_genId_crdate_dict)
	for k,v in linked_folders_genId.items():
		print k, v


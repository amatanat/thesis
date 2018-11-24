#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import collections

def get_app_folder_inode ():
	return root.find("./fileobject/[filename='app']").find('inode').text

def get_data_folder_inode ():
	return root.find("./fileobject/[filename='data']").find('inode').text

def get_folder_data (inode):
	"""Given root folder's inode number
	Find children folders and return a dictionary containing 
	generation id, creation date and inode number of found folders"""
	d = {}
	for fileobject in e.findall('fileobject'):
		# get parent's inode value
		parent_inode = fileobject.find('parent_object').find('i_node').text
		name_type = fileobject.find('name_type').text 
		if (parent_inode is not None and int(parent_inode) == int(inode) and str(name_type) == "d/d"):
			# get folder's creation date, inode and generation id
			crdate = str(fileobject.find('crtime').text).split("T")
			cdate = str(fileobject.find('ctime').text).split("T")
			i_node = int(fileobject.find('inode').text)
			genId = int(fileobject.find('genId').text)
			d[genId] = (crdate[0],i_node,cdate[0],cdate[1],crdate[1].split("Z")[0])
	# sort a dictionary by key
	return collections.OrderedDict(sorted(d.items()))

def link_folders (dict1, dict2, threshold):
	"""Given folders' data
	Link data/app folder to data/data folder
	return a dictionary containing inodes of linked folders,
	inodeAppFolder: inodeDataFolder"""
	linked_inodes = {}
	for key_a, value_a in dict1.items():
		link_prev, link_next, key = dict1._OrderedDict__map[key_a] 
		for key_d, value_d in dict2.items():
			if (key_d > key_a 			and 	# genIdDataFolder > genIdAppFolder1
			    key_d < link_next[2] 		and	# genIdDataFolder < genIdAppFolder2
			    #value_a[0] == value_d[0] 	        and 	# crdateAppFolder == crdateDataFolder
			    key_d - key_a <= threshold):		# genIdDataFolder - genIdAppFolder1 <= threshold
					linked_inodes[value_a[1]] = value_d[1]
					break
		if (value_a[1] not in linked_inodes):
			linked_inodes[value_a[1]] = "unknown"
	return collections.OrderedDict(sorted(linked_inodes.items()))

def link_data_folders (data_folder_data, count, text):
	linked_folders = {}
	for key, value in data_folder_data.items():
		folder_genId = key + count
		for fileobject in e.findall('fileobject'):
			filename = str(fileobject.find('filename').text)
			genId = fileobject.find('genId').text
			if (genId is not None and
			    folder_genId == int(genId) and
			    filename.startswith(text)):
					inode = int(fileobject.find('inode').text)
					linked_folders[value[1]] = inode
					break
	return collections.OrderedDict(sorted(linked_folders.items()))

def get_pre_installed_data_folders (data_folder_data):
	pre_installed_apps = list()
	for value in data_folder_data.values():
		if value[0].startswith("1970"):
			pre_installed_apps.append(value[1])
	return pre_installed_apps

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: python link_folders.py <xml_dump_name>"
		exit()

	xml_dump = sys.argv[1] 
	root = ET.parse(xml_dump).getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	e = ET.fromstring(xmlstr)
	
	app_folder_inode = get_app_folder_inode()
	app_folder_data = get_folder_data(app_folder_inode)

	data_folder_inode = get_data_folder_inode()
	data_folder_data = get_folder_data(data_folder_inode)
	
	linked_data_user_de = link_data_folders(data_folder_data, 3,"user_de")
	print "data->user_de"
	for k,v in linked_data_user_de.items():
		print k,v

	linked_data_misc_cur = link_data_folders(data_folder_data, 6,"misc/")
	print "data->misc/profiles/cur/0"
	for k,v in linked_data_misc_cur.items():
		print k,v
	
	linked_data_misc_ref = link_data_folders(data_folder_data, 8,"misc/")
	print "data->misc/profiles/ref/"
	for k,v in linked_data_misc_ref.items():
		print k,v

	threshold = 130
	linked_folders = link_folders(app_folder_data,data_folder_data, threshold)
	print "app->data"
	for k,v in linked_folders.items():
		print k, v
	



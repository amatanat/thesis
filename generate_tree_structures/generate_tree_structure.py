#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import json
import operator 

generation_id_list = []
count = 0

def reset_count () :
	global count
	count = 0

def find_file_object (inode):
	"""Return a file_object from the tree with the given 'inode' value"""
	text = "./fileobject/[inode=" + "'" + str(inode) + "'" + "]"
	return root.find(text)

def find_children_count (inode, check_folders):
	"""Return children files' count inside the given 'inode' folder
	If 'check_folders' is true then also count files inside folders in the given 'inode' folder"""
	global count 
	reset_count()
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_name_type = fileobject.find('name_type').text 

		if (check_folders and fo_parent_inode is not None and int(fo_parent_inode) == int(inode) 
			and str(fo_name_type) == str("d/d")):

			fo_inode = fileobject.find('inode').text
			count += find_children_count(fo_inode, False)

		elif (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) and 
			str(fo_name_type) == str("r/r")):
			count += 1			
	return count

def find_nephew_count (inode):
	"""Return files' count inside the sibling folders"""
	nephew_count = 0
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_name_type = fileobject.find('name_type').text 

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) 
			and str(fo_name_type) == str("d/d")):
			
			fo_inode = fileobject.find('inode').text
			nephew_count += find_children_count(fo_inode, False)
	return nephew_count 
	

def find_size_order (parent_inode, file_inode):
	"""Create a list containing (inode,size) tuple of files in a given folder. 
	Return size_order of a requested file."""
	inode_size_list = list()
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_name_type = fileobject.find('name_type').text 
		fo_inode = fileobject.find('inode')
		fo_filesize = fileobject.find('filesize')

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and 
			str(fo_name_type) == str("r/r") and fo_inode is not None and fo_filesize is not None and
			fo_inode.text is not None and fo_filesize.text is not None):

			inode_size_list.append((int(fo_inode.text),int(fo_filesize.text)))

		elif (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and
			str(fo_name_type) == str("r/r") and fo_inode is not None and fo_filesize is not None and
			fo_inode.text is not None and fo_filesize.text is None):

			inode_size_list.append((int(fo_inode.text), 0))


	# sort a list by a second value in tuples, i.e by size
	sorted_list = sorted(inode_size_list, key=lambda tup: tup[1])
	
	return [t[0] for t in sorted_list].index(int(file_inode))

def find_depth (fo_inode):
	""" Return depth of the input inode from data/appname folder"""
	depth = 0
    	while fo_inode is not None and int(fo_inode) != data_appname_folder_inode:
        	depth += 1
		fo = find_file_object(fo_inode)
        	fo_inode = fo.find('parent_object').find('i_node').text
    	return depth

def append_to_output (size_order, parent_gen_id_order, sibling_count, uncle_count, nephew_count, cousin_count, depth, mtime, ctime, atime, crtime, filename):
	data = {
		'size order' : size_order,
		'parent gen Id order' : parent_gen_id_order,
		'sibling count' : sibling_count,
		'uncle count' : uncle_count,
		'nephew count' : nephew_count,
		'cousin count' : cousin_count,
		'depth' : depth,
		'mtime' : mtime,
		'ctime' : ctime,
		'atime' : atime,
		'crtime' : crtime,
		'filename' : filename
		}
	output.append(data)


def output_json(filename) :
	with open(filename, 'w+') as outfile:
		json.dump(output, outfile)

def generate_structure (grandparent_inode, parent_inode):
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_name_type = fileobject.find('name_type').text 
		fo_inode =  fileobject.find('inode').text 

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and 
			str(fo_name_type) == str("d/d") and fo_inode is not None): 
			
			generate_structure(fo_parent_inode, fo_inode)

		elif (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and 
			str(fo_name_type) == str("r/r") and fo_inode is not None):

			fo_mtime = get_timestamp (fileobject, 'mtime')
			fo_ctime = get_timestamp (fileobject, 'ctime')
			fo_atime = get_timestamp (fileobject, 'atime')
			fo_crtime = get_timestamp (fileobject, 'crtime')
			
			size_order = find_size_order(fo_parent_inode, fo_inode)

			sibling_count = find_children_count(fo_parent_inode, False) - 1
			nephew_count = find_nephew_count(fo_parent_inode)

			uncle_count = find_children_count(grandparent_inode, False) 

			# we minus sibling files' count, uncle files' count and 1 for this file from result
			# because uncle files' count are also added to the result in the find_children_count function's 'elif' part
			cousin_count = find_children_count(grandparent_inode, True) - sibling_count - uncle_count - 1
		
			parent_gen_id_order = get_gen_id_order(find_file_object(fo_parent_inode).find('genId').text)

			if fbe_encryption:
				filename = None
			else:
				filename = get_filename(fo_inode)
			
			depth = find_depth(fo_inode)
			
			append_to_output(size_order, parent_gen_id_order, sibling_count, uncle_count, nephew_count, cousin_count, depth, fo_mtime, fo_ctime, fo_atime, fo_crtime, filename)

def get_timestamp (fo, name):
	ts_name = fo.find(name)
	if ts_name is not None:
		return ts_name.text

def extract_gen_id (inode):
	global generation_id_list
	for fo in root.findall('fileobject'):
		fo_parent_inode = fo.find('parent_object').find('i_node').text
		fo_name_type = fo.find('name_type').text
		fo_generation_id = fo.find('genId').text
		fo_inode = fo.find('inode').text

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) and
			str(fo_name_type) == str("d/d") and fo_inode is not None and fo_generation_id is not None):
				generation_id_list.append(fo_generation_id)
				extract_gen_id(fo_inode)

	generation_id_list.sort()

def get_gen_id_order (generation_id):
	global generation_id_list
	return 	generation_id_list.index(generation_id)

def extract_filename(inode):
	for fo in root.findall('fileobject'):
		fo_parent_inode = fo.find('parent_object').find('i_node').text
		fo_name_type = fo.find('name_type').text
		fo_inode = fo.find('inode').text
		fo_name = fo.find('filename')

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) and str(fo_name_type) == str("r/r") and 
			fo_inode is not None and fo_name is not None and fo_name.text is not None):
				filename_list.append((int(fo_inode), fo_name.text))

		elif (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) and 
			str(fo_name_type) == str("d/d") and fo_inode is not None):
				extract_filename(fo_inode)
	
def get_filename(inode):
	for item in filename_list:
		if item[0] == int(inode):
			return item[1]

if __name__ == '__main__':
	if len(sys.argv) < 6:
		print "Usage: python generate_tree_structure.py <xml_dump_name> <inode> <parent_inode> <output_file_name> <encryption>"
		exit()

	xml_dump = sys.argv[1]
	inode = sys.argv[2]
	parent_inode = sys.argv[3]
	output_filename = sys.argv[4]
	fbe_encryption = sys.argv[5] == 'FBE'
	root = ET.parse(xml_dump).getroot()
	data_appname_folder_inode = int(inode)

	if not fbe_encryption:
		filename_list = list()
		extract_filename(inode)
		
	# append data/com.appname folder's gen id to the generation id list
	generation_id_list.append(find_file_object(inode).find('genId').text)
	extract_gen_id(inode)

	output = []
	generate_structure(parent_inode,inode)

	# sort a final result by files' depth
	output.sort(key = lambda k: k['depth'])

	output_json(output_filename + ".json")


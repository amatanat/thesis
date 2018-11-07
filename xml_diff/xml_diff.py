#! /usr/bin/env python

import sys
import json
import xml.etree.ElementTree as ET
from file_object import file_object
from datetime import datetime

new_files = set()
renamed_files = set()
moved_files = set()
changed_metadata = set()
deleted_files = set()

def get_file_objects_dict (root):
	file_objects_dict = {}
	for fo in root.findall('fileobject'):
		parent_inode = fo.find('parent_object').find('i_node')
		if parent_inode is not None:
			parent_inode = fo.find('parent_object').find('i_node').text
		filename = fo.find('filename').text
		name_md5 = fo.find('name_md5').text
		name_B64 = fo.find('name_B64').text
		name_type = fo.find('name_type').text 
		filesize = fo.find('filesize').text 
		inode = fo.find('inode').text
		mode = fo.find('mode').text
		nlink = fo.find('nlink').text
		namesize = fo.find('nameSize').text
		uid = fo.find('uid').text
		gid = fo.find('gid').text
		genId = fo.find('genId').text
		mtime = fo.find('mtime')
		if mtime is not None:
			mtime = fo.find('mtime').text 
		atime = fo.find('atime') 
		if atime is not None:
			atime = fo.find('atime') .text
		ctime = fo.find('ctime')
		if ctime is not None:
			ctime = fo.find('ctime').text 
		crtime = fo.find('crtime')
		if crtime is not None:
			crtime = fo.find('crtime').text
		xnonce = fo.find('xnonce')
		if xnonce is not None:
			xnonce = fo.find('xnonce').text
		xmaster = fo.find('xmaster')
		if xmaster is not None:
			xmaster = fo.find('xmaster').text
		xNameCipher = fo.find('xNameCipher')
		if xNameCipher is not None:
			xNameCipher = fo.find('xNameCipher').text
		
		fileobject = file_object(filename, name_md5, name_B64, name_type, filesize, inode, parent_inode, mode, nlink, namesize, uid, gid,genId, mtime, atime, ctime, crtime, xnonce, xmaster, xNameCipher)
		
		file_objects_dict[inode] = fileobject

	return file_objects_dict

def compare_dictionaries (old, new):
	for key, n_fo in new.items():
		if key in old:
			o_fo = old[key]
			if n_fo["parent_inode"] != o_fo["parent_inode"]:
				moved_files.add((o_fo, n_fo))
			elif n_fo["filename"] != o_fo["filename"]:
				renamed_files.add((o_fo, n_fo))
			elif not (n_fo["mtime"] == o_fo["mtime"] or 
				n_fo["atime"] == o_fo["atime"] or 
				n_fo["ctime"] == o_fo["ctime"] or
				n_fo["crtime"] == o_fo["crtime"]):
					changed_metadata.add((o_fo, n_fo))
			# delete already processed key,value from dictionary
			del old[key]
		else:
			# inode is not present in first xml dump, that means it is a new file
			new_files.add(n_fo)
	if len(old) > 0:
		# file objects present in first xml dump and not in second xml dump are the deleted ones
		global deleted_files
		deleted_files = old.values()

def get_datetime (str_datetime):
	"""Get datetime in iso format"""
	datetime_object = datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%SZ')
	return datetime_object.isoformat(' ')

def get_file_objects_data (fileobjects):
	"""Take a set of file_objects as input and
	return a sorted set containing: ('mtime', 'inode') for each file_object""" 
	result = set()
	for fo in fileobjects:
		result.add((get_datetime(fo["mtime"]), fo["inode"]))
	return sorted(result)

def get_file_objects2_data (fileobjects):
	"""Take a set containing tuples of file_objects as input
	 for each tuple: compare file_objects data
	 return a sorted set containing different data"""
	result = set()
	for (o_fo, n_fo) in fileobjects:
		if o_fo["filename"] != n_fo["filename"]:				
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "filename changed"))

		if o_fo["parent_inode"] != n_fo["parent_inode"]:
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "file moved, parent inode changed", o_fo["parent_inode"], 
			n_fo["parent_inode"]))

		if o_fo["mtime"] != n_fo["mtime"]:
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "mtime changed", get_datetime(o_fo["mtime"])))

		if o_fo["atime"] != n_fo["atime"]:
			result.add((get_datetime(n_fo["atime"]), n_fo["inode"], "atime changed", get_datetime(o_fo["atime"])))

		if o_fo["ctime"] != n_fo["ctime"]:
			result.add((get_datetime(n_fo["ctime"]), n_fo["inode"], "ctime changed", get_datetime(o_fo["ctime"])))

		if o_fo["crtime"] != n_fo["crtime"]:
			result.add((get_datetime(n_fo["crtime"]), n_fo["inode"], "crtime changed", get_datetime(o_fo["crtime"])))

	return sorted(result)

def append_to_output (key, value, output_data):
	"""Append a new key and value to an output data"""
	output_data[key] = []
	for fo in value:
		data = {
			'datetime' : str(fo[0]),
			'inode' : str(fo[1])
			}
		output_data[key].append(data)	

def append_to_output2 (key, value, output_data):
	output_data[key] = []
	for fo in value:
		if len(fo) == 3:
			data = {
				'datetime' : str(fo[0]),
				'inode' : str(fo[1]),
				'action': str(fo[2])
				}
		elif len(fo) == 4:
			data = {
				'datetime' : str(fo[0]),
				'inode' : str(fo[1]),
				'action': str(fo[2]),
				'previous_datetime' : str(fo[3])
				}
		elif len(fo) == 5:
			data = {
				'datetime' : str(fo[0]),
				'inode' : str(fo[1]),
				'action': str(fo[2]),
				'previous_parent_inode' : str(fo[3]),
				'current_parent_inode' : str(fo[4])
				}
		output_data[key].append(data)	

def output_json(filename) :
	
	output_data = {}
	append_to_output('New files', get_file_objects_data(new_files), output_data)
	append_to_output('Deleted files', get_file_objects_data(deleted_files), output_data)
	append_to_output2("Renamed files:", get_file_objects2_data(renamed_files), output_data)
	append_to_output2("Moved files:", get_file_objects2_data(moved_files), output_data)
	append_to_output2("Changed metadata:", get_file_objects2_data(changed_metadata), output_data)

	with open(filename, 'w+') as outfile:
    		json.dump(output_data, outfile)
	

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Usage: python pretty_print.py <first_xml_dump_name> <second_xml_dump_name> <output file name>"
		print "<first_xml_dump_name> xml dump before an action" 
		print "<second_xml_dump_name> xml dump after an action"
		exit()

	first_xml_dump = sys.argv[1] 
	first_root = ET.parse(first_xml_dump).getroot()
	old = get_file_objects_dict(first_root)
	
	second_xml_dump = sys.argv[2] 
	second_root = ET.parse(second_xml_dump).getroot()
	new = get_file_objects_dict(second_root)

	output_filename = sys.argv[3]

	compare_dictionaries(old, new)

	output_json(output_filename + ".json")
			


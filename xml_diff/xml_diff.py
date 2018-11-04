#! /usr/bin/env python

import sys
import xml.etree.ElementTree as ET
from file_object import file_object
from datetime import datetime

new_files = set()
renamed_files = set()
moved_files = set()
changed_metadata = set()
deleted_files = set()

def get_file_object_dict (root, file_object_dict):
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
		
		file_object_dict[inode] = fileobject

	return file_object_dict

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

def print_set (data):
	"""Print set without comma and brackets"""
	for i in data:
		print ' '.join([str(k) for k in i]) 

def print_file_objects (title, file_objects):
	print "\n" + title +  "\n"
	result = set()
	for fo in file_objects:
		result.add((get_datetime(fo["mtime"]), fo["inode"]))
	print_set(sorted(result))

def print_file_objects2 (title, file_objects):
	print "\n" + title +  "\n"
	result = set()
	for (o_fo, n_fo) in file_objects:
		if o_fo["filename"] != n_fo["filename"]:				
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "filename changed"))

		if o_fo["parent_inode"] != n_fo["parent_inode"]:
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "file moved, parent inode changed", o_fo["parent_inode"], "=>", n_fo["parent_inode"]))

		if o_fo["mtime"] != n_fo["mtime"]:
			result.add((get_datetime(n_fo["mtime"]), n_fo["inode"], "mtime changed", get_datetime(o_fo["mtime"]), "=>",get_datetime(n_fo["mtime"])))

		if o_fo["atime"] != n_fo["atime"]:
			result.add((get_datetime(n_fo["atime"]), n_fo["inode"], "atime changed", get_datetime(o_fo["atime"]), "=>", get_datetime(n_fo["atime"])))

		if o_fo["ctime"] != n_fo["ctime"]:
			result.add((get_datetime(n_fo["ctime"]), n_fo["inode"], "ctime changed", get_datetime(o_fo["ctime"]), "=>", get_datetime(n_fo["ctime"])))

		if o_fo["crtime"] != n_fo["crtime"]:
			result.add((get_datetime(n_fo["crtime"]), n_fo["inode"], "crtime changed", get_datetime(o_fo["crtime"]), "=>", get_datetime(n_fo["crtime"])))

	print_set (sorted(result))

def final_report() :
	print_file_objects("New files:", new_files)
	print_file_objects("Deleted files:", deleted_files)
	print_file_objects2("Renamed files:", renamed_files)
	print_file_objects2("Moved files:", moved_files)
	print_file_objects2("Changed metadata:", changed_metadata)	
	

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "Usage: python pretty_print.py <first_xml_dump_name> <second_xml_dump_name>"
		print "<first_xml_dump_name> xml dump before an action" 
		print "<second_xml_dump_name> xml dump after an action"
		exit()

	first_xml_dump = sys.argv[1] 
	first_root = ET.parse(first_xml_dump).getroot()
	old = {}
	old = get_file_object_dict(first_root, old)
	
	second_xml_dump = sys.argv[2] 
	second_root = ET.parse(second_xml_dump).getroot()
	new = {}
	new = get_file_object_dict(second_root, new)

	compare_dictionaries(old, new)

	final_report()
			


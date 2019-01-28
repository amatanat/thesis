#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
import re
from collections import Counter 
import json
import subprocess

def connect_to_db (db_file):
	""" create a database connection to the SQLite database
        specified by the db_file
    	return: Connection object or None """
    	try:
        	conn = sqlite3.connect(db_file)
        	return conn
    	except Error as e:
        	print(e)
	return None

def get_app_ids (db):
	""" Return all applications' ID from a db """
	ids = list()
	cursor = db.cursor()
	sql_select = "SELECT ID FROM applications"
	cursor.execute(sql_select)
	
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			ids.append(int(item))
	return ids

def get_app_name (db, app_id):
	""" Return application name with the given app_id """
	cursor = db.cursor()
	sql_select = "SELECT name, version FROM applications WHERE ID=?"
	cursor.execute(sql_select, (app_id,))
	rows = cursor.fetchall()
    	for row in rows:
		return row

def get_fingerprints_size (db, app_id, file_type):
	""" Get fingerprints' size list from a db with the 
	given app_id and file_type """
	size_list = list()
	cursor = db.cursor()
	sql_select = "SELECT file_size FROM fingerprints WHERE application_id=? AND file_type=?"
	cursor.execute(sql_select, (app_id,file_type,))
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			size_list.append(int(item))
	return size_list

def compare (s, t):
    return Counter(s) == Counter(t)	

def extract_fingerprints_size (fingerprint_type, fingerprints):
	""" Extract fingerprints' size with the given type
	from a given list """
	fingerprints_size = list()
	for i in fingerprints:
		if (i[2] == fingerprint_type):
			fingerprints_size.append(i[1])
	return fingerprints_size

def match_data (db, fingerprint_type, fingerprints, file_type):
	""" Return app_id if fingerprint match is found in a db"""
	fingerprints_size = extract_fingerprints_size(fingerprint_type, fingerprints)
	app_ids = get_app_ids(db)
	for app_id in app_ids:
		db_app_fingerprints_size = get_fingerprints_size(db, app_id, file_type)
		if compare(db_app_fingerprints_size,fingerprints_size):
			return app_id

def get_app (db, lib_app_id, root_app_id):
	""" Return app_name if all app ids are equal,
	i.e all fingerprints belong to the same app in a db """
	if (lib_app_id == root_app_id):
		return get_app_name(db, root_app_id)

def find_matches (fingerprints):
	""" Return an app name if match is found in a db for given fingerprints """

	root_app_id = match_data(db, 'root', fingerprints, 'root') 	
	
	# if both 'lib' and 'oat' contain 2 or 3 files
	if (any(e[2] == 'unknown' for e in fingerprints)):
	
		# match 'unknown' with 'lib' files
		lib_app_id_one = match_data(db, 'unknown', fingerprints, 'lib')
		app_name_one = get_app(db, lib_app_id_one, root_app_id)
		
		# match 'oat' with 'lib' files			
		lib_app_id_two = match_data(db, 'oat', fingerprints, 'lib')
		app_name_two = get_app(db, lib_app_id_two, root_app_id) 

		if app_name_one is not None and app_name_two is not None:
			return (app_name_one, app_name_two)	
		if app_name_one is not None:
			return app_name_one
		if app_name_two is not None:
			return app_name_two
	 
	# if any 'lib' file is available
	if (any(e[2] == 'lib' for e in fingerprints)):	
		lib_app_id = match_data(db, 'lib', fingerprints, 'lib')

		app_name = get_app(db, lib_app_id, root_app_id)
		if app_name is not None:
			return app_name

	# no 'lib' file, only 'root' file is available
	if (root_app_id is not None):
		return get_app_name(db, root_app_id)

def output_result(result):
	with open(output, 'w+') as f:
     		f.write(json.dumps(result))

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python identify_installed_apps.py <fingerprints_db_name> <xml_dump_name> <xml_extracted_fingerprints_name> <output_file_name>"
		exit()

	db_file_name = sys.argv[1] 
	xml_dump = sys.argv[2]
	xml_extracted_fingerprints_name = sys.argv[3]
	output =  sys.argv[4] + ".json"
 
	subprocess.call(["python", "xml_fingerprints_extractor.py", xml_dump, xml_extracted_fingerprints_name])
	xml_extracted_fingerprints = xml_extracted_fingerprints_name + ".txt"
	
	db = connect_to_db(db_file_name)
	if db is not None:
		with open(xml_extracted_fingerprints, 'r') as f:
    			data = json.load(f)
			app_name_dict = {}

			for key, value in data.items():
				app_name = find_matches(value)
				if app_name is not None:
					app_name_dict[key] = app_name

			# if any match is found
			if (len(app_name_dict)) > 0 :
				# output result to json file
				output_result(app_name_dict)
		
	else:
        	print("Error! Cannot connect to a DB")
	


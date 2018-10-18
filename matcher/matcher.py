#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
import re
from collections import Counter 
import json

def connect_to_db (db_file):
	""" create a database connection to the SQLite database
        specified by the db_file
    	return: Connection object or None"""
    	try:
        	conn = sqlite3.connect(db_file)
		print "connected to db.."
        	return conn
    	except Error as e:
        	print(e)
	return None

def get_app_ids (db):
	ids = list()
	cursor = db.cursor()
	sql_select = "SELECT ID FROM application"
	cursor.execute(sql_select)
	
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			ids.append(int(item))
	return ids

def get_app_name (db, app_id):
	cursor = db.cursor()
	sql_select = "SELECT name FROM application WHERE ID=?"
	cursor.execute(sql_select, (app_id,))
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			return item

def get_profiles_size (db,app_id):
	size_list = list()
	cursor = db.cursor()
	sql_select = "SELECT file_size FROM profile WHERE application_id=?"
	cursor.execute(sql_select, (app_id,))
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			size_list.append(int(item))
	return size_list

def compare (s, t):
    return Counter(s) == Counter(t)	

def match_data (db, files_size):
	app_ids = get_app_ids(db)
	for app_id in app_ids:
		l = get_profiles_size(db,app_id)
		if compare(l,files_size):
			return get_app_name(db,app_id)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python matcher.py <application_profiles_db_name> <xml_extracted_files_size_filename>"
		exit()

	db_file_name = sys.argv[1] 
	xml_extracted_files_size = sys.argv[2]

	db = connect_to_db(db_file_name)
	if db is not None:
		with open(xml_extracted_files_size, 'r') as f:
    			data = json.load(f)
			app_name_dict = {}
			for key, value in data.items():
				files_size = list()
				for i in value:				
					files_size.append(i[1])
				app_name = match_data(db, files_size)
				if app_name is not None:
					app_name_dict[key] = app_name

			for k,v in app_name_dict.items():
				print k,v
		
	else:
        	print("Error! Cannot connect to a DB")
	


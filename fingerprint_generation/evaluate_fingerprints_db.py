#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
import json


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

def find_count(db, query):
	cursor = db.cursor()
	cursor.execute(query)
	rows = cursor.fetchall()
	for row in rows:
		for item in row:
			return item

def find_ids (db):
	"""This function returns application ids those do not have unique fingerprints."""
	id_list = list()
	query = """select application_id from fingerprints where file_type='root' and file_size in (select file_size from fingerprints where file_type='root' group by file_size having count(file_size) > 1) INTERSECT select application_id from fingerprints where file_type='lib' and file_size in (select file_size from fingerprints where file_type='lib' group by file_size having count(file_size) > 1);"""
	cursor = db.cursor()
	cursor.execute(query)
	rows = cursor.fetchall()
    	for row in rows:
		for item in row:
			id_list.append(int(item))
	return id_list

def get_app_data (db, app_id):
	result = list()
	query = """select file_name, file_size, file_type from fingerprints where application_id=?"""
	cursor = db.cursor()
	cursor.execute(query, [app_id])
	rows = cursor.fetchall()
	for row in rows:
		result.append(row)
	return result

def get_app_name (db, app_id):
	query = """select name from applications where ID=?"""
	cursor = db.cursor()
	cursor.execute(query, [app_id])
	rows = cursor.fetchall()
	for row in rows:
		for item in row:
			return item

def find_apps_with_same_fings (db, app_id_list):
	"""This function returns a dictionary containing app IDs with the same fingerprints"""
	result = {}
	for app_id in app_id_list:
		app_data = get_app_data(db, app_id)

		for application_id in app_id_list:

			if app_id != application_id:
				application_data = get_app_data(db, application_id)
	
				if set(app_data) == set(application_data):

					if not (application_id in result and app_id == result[application_id]):
						if app_id in result:
							result[app_id] = [result[app_id], application_id]
						else:
							result[app_id] = application_id
	return result

def find_same_apps (db, app_id_list_dict):
	"""This function returns the name, version IDs of apps that have same fingerprints for different versions"""
	result = {}
	for key, value in app_id_list_dict.items():
		key_app_name = get_app_name (db, key)
		value_app_name =  get_app_name (db, value)
		if key_app_name == value_app_name:
			result[key] = (key_app_name, value)
	return result

def output_result(result):
	with open(output_filename, 'w+') as f:
     		f.write(json.dumps(result))

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python evaluate_fingerprints_db.py <fingerprints_db_name> <output_filename>"
		exit()
	db_file_name = sys.argv[1] 
	output_filename = sys.argv[2]

	db = connect_to_db(db_file_name)

	distinct_app_count_query = """select count(distinct name) from applications;"""
	total_apk_count_query = """select count(name) from applications;"""

	if db is not None:
		output = {}

		total_apk_count = find_count(db, total_apk_count_query)
		output["total_apk_count"] = total_apk_count

		distinct_app_count = find_count(db, distinct_app_count_query)
		output["distinct_app_count"] = distinct_app_count
		
		# find app ids that do not have unique fingerprints
		app_id_list = find_ids(db)
		# find apps with the same fingerprints
		apps_with_same_fings = find_apps_with_same_fings(db, app_id_list)
		# find app versions with the same fingerprints
		app_versions_with_same_fings = find_same_apps(db, apps_with_same_fings)

		if len(apps_with_same_fings) > 0:
			output["app_ids_with_same_fingerprints"] = apps_with_same_fings

		if len(app_versions_with_same_fings) > 0:
			output["app_versions_with_same_fingerprints"] = app_versions_with_same_fings

		output_result(output)

	else:
	       	print("Error! Cannot connect to a DB")



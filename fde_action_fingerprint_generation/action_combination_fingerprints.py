#!/usr/bin/env python

import sys
import ast
import sqlite3
from sqlite3 import Error

def connect_to_db (db_file):
	""" create a database connection to the SQLite database
        specified by the db_file
    	return: Connection object or None"""
    	try:
        	conn = sqlite3.connect(db_file)
        	return conn
    	except Error as e:
        	print(e)
	return None

def insert_action_combination_fingerprints (db, app_name, action_name, action_name_list, path, changed): 
	sql_insert = """INSERT INTO action_combination_fingerprints (app_name, action_name, included_actions, path, changed)
		      VALUES(?,?,?,?,?)"""
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (app_name, action_name, str(action_name_list), path, changed))
   	return cursor.lastrowid

def find_action_combination_fingerprints(db, app_name, action_name, action_name_list):
	placeholders= ', '.join(['?'] * len(action_name_list))
	query = ''' SELECT app_name, action_name, path, changed
		        FROM action_fingerprints
		        WHERE action_fingerprints.action_name = {}
			AND action_fingerprints.app_name = {}
			AND action_fingerprints.path IN (
				SELECT path
				FROM action_fingerprints AS fingerprints
				WHERE fingerprints.app_name = action_fingerprints.app_name
					AND fingerprints.changed = action_fingerprints.changed
					AND fingerprints.action_name IN ({})
				)
			ORDER BY id ASC;'''.format("'"+action_name+"'", "'"+app_name+"'", placeholders)

	cursor = db.cursor()
	cursor.execute(query, tuple(action_name_list))
	return cursor.fetchall()

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python action_combination_fingerprints.py <db_filename> <app_name> <action_name> <action_name_list>"
		exit()

	db_filename = sys.argv[1] 
	app_name = sys.argv[2]
	action_name = sys.argv[3]
	action_name_list = ast.literal_eval(sys.argv[4])

	db = connect_to_db(db_filename)
	if db is not None:
		rows = find_action_combination_fingerprints(db, app_name, action_name, action_name_list)
		for row in rows:
			insert_action_combination_fingerprints (db, app_name, action_name, action_name_list, row[2], row[3])
		db.commit()
		
	else:
        	print("Error! Cannot connect to a DB")




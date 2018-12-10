#!/usr/bin/env python

import sys
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

def insert_action_subtraction_fingerprints (db, app_name, first_action_name, second_action_name, path, changed): 
	sql_insert = """INSERT INTO action_subtraction_fingerprints (app_name, first_action_name, second_action_name, path, changed)
		      VALUES(?,?,?,?,?)"""
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (app_name, first_action_name, second_action_name, path, changed))
   	return cursor.lastrowid

def find_action_subtraction_fingerprints(db, query, app_name, first_action_name, second_action_name):
	cursor = db.cursor()
	cursor.execute(query, [first_action_name, app_name, second_action_name, app_name])
	return cursor.fetchall()

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python action_fingerprints_generation.py <db_filename> <app_name> <action_name_1> <action_name_2>"
		exit()

	db_filename = sys.argv[1] 
	app_name = sys.argv[2]
	first_action_name = sys.argv[3]
	second_action_name = sys.argv[4]

	query = """SELECT app_name, action_name, path, changed
		        FROM action_fingerprints
		        WHERE action_fingerprints.action_name = ? 
			AND action_fingerprints.app_name = ?
			AND action_fingerprints.path NOT IN (
				SELECT path
				FROM action_fingerprints AS fingerprints
				WHERE fingerprints.action_name = ? 
					AND fingerprints.app_name = ?
					AND action_fingerprints.changed = fingerprints.changed
				)
			ORDER BY id ASC;"""


	db = connect_to_db(db_filename)
	if db is not None:
		rows = find_action_subtraction_fingerprints(db, query, app_name, first_action_name, second_action_name)
		for row in rows:
			insert_action_subtraction_fingerprints (db, app_name, first_action_name, second_action_name, row[2], row[3])
		db.commit()
		
	else:
        	print("Error! Cannot connect to a DB")




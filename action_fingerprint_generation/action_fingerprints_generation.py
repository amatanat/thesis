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

def insert_action_fingerprints (db, app_name, action_name, path, changed): 
	sql_insert = "INSERT INTO action_fingerprints (app_name, action_name, path, changed) VALUES(?,?,?,?)"
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (app_name, action_name, path, changed))
   	return cursor.lastrowid

def find_action_fingerprints (db, sql_query, app_name, action_name):
	cursor = db.cursor()
	cursor.execute(sql_query,  [action_name, app_name, action_name, app_name])
	return cursor.fetchall()

def get_all_action_fingerprints (db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM action_fingerprints")
    rows = cursor.fetchall()
    for row in rows:
	print(row)

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Usage: python action_fingerprints_generation.py <db_filename> <app_name> <action_name>"
		exit()

	db_filename = sys.argv[1] 
	app_name = sys.argv[2]
	action_name = sys.argv[3]

	sql_query =  """SELECT count(*), app_name, action_name, path, changed 
		        FROM action_profiles
		        WHERE action_profiles.action_name = ? 
			AND action_profiles.app_name = ?
			GROUP BY path, changed
			HAVING count (*) = (
				SELECT MAX(run)
				FROM action_profiles AS profiles
				WHERE profiles.action_name = ?
				AND profiles.app_name = ? 
			)
			ORDER BY id ASC;"""

	db = connect_to_db(db_filename)
	if db is not None:
		rows = find_action_fingerprints(db, sql_query, app_name, action_name)
		for row in rows:
			insert_action_fingerprints (db, app_name, action_name, row[3], row[4])
		db.commit()
		
	else:
        	print("Error! Cannot connect to a DB")




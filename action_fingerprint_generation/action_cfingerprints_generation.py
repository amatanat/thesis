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

def insert_action_cfingerprints (db, app_name, action_name, key, changed, inode): 
	sql_insert = "INSERT INTO action_cfingerprints (app_name, action_name, key, changed, inode) VALUES(?,?,?,?,?)"
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (app_name, action_name, key, changed, inode))
   	return cursor.lastrowid

def find_action_cfingerprints (db, sql_query, app_name, action_name):
	cursor = db.cursor()
	cursor.execute(sql_query, [action_name, app_name, action_name, app_name])
	return cursor.fetchall()

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Usage: python action_fingerprints_generation.py <db_filename> <app_name> <action_name>"
		exit()

	db_filename = sys.argv[1] 
	app_name = sys.argv[2]
	action_name = sys.argv[3]

	query = """SELECT app_name, inode, changed, action_name, key 
		        FROM action_fingerprints
		        WHERE action_fingerprints.action_name = ? 
			AND action_fingerprints.app_name = ?
			AND action_fingerprints.inode NOT IN (
				SELECT inode
				FROM action_fingerprints AS profiles_1
				WHERE profiles_1.action_name != ? 
					AND profiles_1.app_name = ?
					AND action_fingerprints.changed = profiles_1.changed
					AND action_fingerprints.key = profiles_1.key
				)
			ORDER BY id ASC;"""

	db = connect_to_db(db_filename)
	if db is not None:
		rows = find_action_cfingerprints(db, query, app_name, action_name)
		for row in rows:
			insert_action_cfingerprints (db, app_name, action_name, row[4], row[2], row[1])
		db.commit()
		
	else:
        	print("Error! Cannot connect to a DB")




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

def insert_action_combination_fingerprints (db, app_name,  included_actions, excluded_actions, path, changed):
	sql_insert = """INSERT INTO action_combination_fingerprints (app_name, included_actions, excluded_actions, path, changed)
		      VALUES(?,?,?,?,?)"""
   	cursor = db.cursor()
 	cursor.execute(sql_insert, (app_name, str(included_actions), str(excluded_actions), path, changed))
   	return cursor.lastrowid

def find_action_combination_fingerprints(db,  included_actions, excluded_actions):
	in_placeholder = ', '.join(['?'] * len(included_actions))
	not_in_placeholder = ', '.join(['?'] * len(excluded_actions))
	query = ''' SELECT app_name, action_name, path, changed, count(*)
		        FROM action_fingerprints
		        WHERE action_fingerprints.action_name in ({})
			AND action_fingerprints.path NOT IN (
				SELECT path
				FROM action_fingerprints AS fingerprints
				WHERE fingerprints.app_name = action_fingerprints.app_name
					AND fingerprints.changed = action_fingerprints.changed
					AND fingerprints.action_name IN ({})
				)
			GROUP BY path, changed
			HAVING count(*) = {}
			ORDER BY id ASC;'''.format(in_placeholder, not_in_placeholder, len(included_actions))

	actions_list = list()
	for action in included_actions:
		actions_list.append(action)
	for action in excluded_actions:
		actions_list.append(action)
	cursor = db.cursor()
	cursor.execute(query, tuple(actions_list))
	return cursor.fetchall()

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Usage: python action_combination_fingerprints.py <db_filename> <included_actions> <excluded_actions> <app_name>"
		exit()

	db_filename = sys.argv[1] 
	included_actions = ast.literal_eval(sys.argv[2])
	excluded_actions = ast.literal_eval(sys.argv[3])
	app_name = sys.argv[4]

	db = connect_to_db(db_filename)
	if db is not None:
		rows = find_action_combination_fingerprints(db, included_actions, excluded_actions)
		for row in rows:
			insert_action_combination_fingerprints (db, app_name, included_actions, excluded_actions, row[2], row[3])
		db.commit()
		
	else:
        	print("Error! Cannot connect to a DB")




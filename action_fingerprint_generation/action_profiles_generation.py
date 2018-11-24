#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
import json

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

def create_table (db, sql_create_table):
	""" create a table from the sql_create_table statement"""
	try:
        	cursor = db.cursor()
        	cursor.execute(sql_create_table)
    	except Error as e:
        	print(e) 

def insert_action_profiles (db, app_name, action_name, key, changed, inode, run):
    	sql_insert = "INSERT INTO action_profiles (app_name, action_name, key, changed, inode, run) VALUES(?,?,?,?,?,?)"
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (app_name, action_name, key, changed, inode, run))
	print "insert into action_profiles table done.."
   	return cursor.lastrowid

def get_all_action_profiles (db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM action_profiles")
    rows = cursor.fetchall()
    for row in rows:
	print(row)

def insert_into_db (db, data, app_name, action_name, run):
	for key, value in data.items(): 
		for j in value:
			changed = j['action'] if 'action' in j else None
			inode = j['inode']
			insert_action_profiles(db, app_name, action_name, key, changed, inode, run)

if __name__ == '__main__':
	if len(sys.argv) < 6:
		print "Usage: python action_profiles_generation.py <db_filename> <json_dump_name> <app_name> <action_name> <run_count>"
		exit()

	db_filename = sys.argv[1] 
	json_dump = sys.argv[2] 
	app_name = sys.argv[3]
	action_name = sys.argv[4]
	run = sys.argv[5] 

	sql_create_action_profiles_table = """create TABLE action_profiles (
                                    ID INTEGER PRIMARY KEY NOT NULL,
				    app_name TEXT NOT NULL,
                                    action_name TEXT NOT NULL,
				    key TEXT NOT NULL,
				    changed TEXT,
				    inode INT NOT NULL,
				    run INT NOT NULL                                
                                );"""

	sql_create_action_fingerprints_table = """create TABLE action_fingerprints (
                                    ID INTEGER PRIMARY KEY NOT NULL,
				    app_name TEXT NOT NULL,	
                                    action_name TEXT NOT NULL,
				    key TEXT NOT NULL,
				    changed TEXT,
				    inode INT NOT NULL                              
                                );"""
	sql_create_action_cfingerprints_table = """create TABLE action_cfingerprints (
                                    ID INTEGER PRIMARY KEY NOT NULL,
				    app_name TEXT NOT NULL,	
                                    action_name TEXT NOT NULL,
				    key TEXT NOT NULL,
				    changed TEXT,
				    inode INT NOT NULL                              
                                );"""
	

	db = connect_to_db(db_filename)
	if db is not None:
		create_table(db, sql_create_action_fingerprints_table)
		create_table(db, sql_create_action_profiles_table)
		create_table(db, sql_create_action_cfingerprints_table)
		with open(json_dump, "r") as f:
  			data = json.loads(f.read())
			insert_into_db(db, data, app_name, action_name, run)
			db.commit()	
	else:
        	print("Error! Cannot connect to a DB")
	


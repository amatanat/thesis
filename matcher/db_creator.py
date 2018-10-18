#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
from collections import Counter 
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
		#print "create table done.."
    	except Error as e:
        	print(e) 

def insert_application (db, application):
    	"""Insert a new application into the application table
    	return an application id"""

    	sql_insert = "INSERT INTO application (name) VALUES(?)"
    	cursor = db.cursor()
    	cursor.execute(sql_insert, [application]) 
	#print "insert into application table done.."
    	return cursor.lastrowid

def insert_profile (db, file_name, file_size, application_id):
    	"""Insert a new profile data into the profile table
	  return a profile id"""

    	sql_insert = "INSERT INTO profile (file_name, file_size, application_id) VALUES(?,?,?)"
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (file_name,file_size,application_id))
	#print "insert into profile table done.."
   	return cursor.lastrowid

def get_all_profiles (db):
    """print all rows in the 'profile' table"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM profile")
    rows = cursor.fetchall()
    for row in rows:
	print(row)

def get_all_applications (db):
    """print all rows in the 'application' table"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM application")
    rows = cursor.fetchall()
    for row in rows:
        print str(row)

def insert_into_db (db, filename):
	app_id = 0
	with open(filename) as ins:
    		for line in ins:
			line = line.rstrip()
			if "name-" in line:
				app_name = line.split("name-")[1]
				app_id = insert_application(db, app_name)
			else:
				line = line.split(" ")
				file_size = int(line[0])
				file_name = line[1]
				file_app_id = app_id
				insert_profile(db, file_name, file_size, file_app_id)	

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python db_creator.py <application_profiles_db_name> <device_extracted_apps_profile_filename> "
		exit()

	db_file_name = sys.argv[1] 
	input_file = sys.argv[2]
	
	sql_create_application_table = """ create TABLE application (
                                        ID INTEGER PRIMARY KEY NOT NULL,
                                        name TEXT NOT NULL
                                        ); """

	sql_create_profile_table = """create TABLE profile (
                                    ID INTEGER PRIMARY KEY NOT NULL,
                                    file_name TEXT NOT NULL,
				    file_size INT NOT NULL,
                                    application_id INTEGER NOT NULL,
                                    FOREIGN KEY (application_id) REFERENCES application (ID)
                                );"""

	db = connect_to_db(db_file_name)
	if db is not None:
		create_table(db, sql_create_profile_table)
        	create_table(db, sql_create_application_table)
		insert_into_db(db, input_file)
		db.commit()		
	else:
        	print("Error! Cannot connect to a DB")
	


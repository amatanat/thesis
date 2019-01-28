#!/usr/bin/env python

import sys
import sqlite3
from sqlite3 import Error
import subprocess

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

def insert_application (db, application, version):
    	"""Insert a new application into the 'applications' table
    	return an application id"""

	sql_insert = "INSERT OR IGNORE INTO applications (name, version) VALUES(?,?)"
    	cursor = db.cursor()
	cursor.execute(sql_insert, (application, version))
	sql_select = "SELECT ID FROM applications WHERE name = ? AND version = ?"
	rows = cursor.execute(sql_select, (application, version))
	for row in rows:
		return row[0]

def insert_fingerprint (db, file_name, file_size, file_type, application_id):
    	"""Insert a new fingerprint data into the 'fingerprints' table
	  return a fingerprint id"""

	sql_insert = "INSERT OR IGNORE INTO fingerprints (file_name, file_size, file_type, application_id) VALUES(?,?,?,?)"
   	cursor = db.cursor()
    	cursor.execute(sql_insert, (file_name,file_size,file_type,application_id))
   	return cursor.lastrowid

def get_all_fingerprints (db):
    """print all rows in the 'fingerprints' table"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM fingerprints")
    rows = cursor.fetchall()
    for row in rows:
	print(row)

def get_all_applications (db):
    """print all rows in the 'applications' table"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM applications")
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
			elif "versionName=" in line:
				version = line.strip().split("=")[1]
				app_id = insert_application(db, app_name, version)
			else:
				line = line.split(" ")
				file_size = int(line[0])
				file_name = line[1]
				file_type = 'lib' if file_name.startswith('lib') else 'root'
				insert_fingerprint(db, file_name, file_size, file_type, app_id)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: python fingerprint_generation.py <application_fingerprints_db_name>"
		exit()

	subprocess.call(['./device_app_fingerprints_extractor.sh'])

	db_file_name = sys.argv[1] 
	app_fingerprints = "device_app_fingerprints.txt"
	
	sql_create_applications_table = """CREATE TABLE IF NOT EXISTS applications (
                                        ID INTEGER PRIMARY KEY NOT NULL,
                                        name TEXT NOT NULL,
					version TEXT NOT NULL,
					UNIQUE(name, version)
                                        ); """

	sql_create_fingerprints_table = """CREATE TABLE IF NOT EXISTS fingerprints (
                                    ID INTEGER PRIMARY KEY NOT NULL,
                                    file_name TEXT NOT NULL,
				    file_size INT NOT NULL,
				    file_type TEXT NOT NULL,
                                    application_id INTEGER NOT NULL,
				    UNIQUE(file_name, file_size, file_type, application_id),
                                    FOREIGN KEY (application_id) REFERENCES applications (ID)
                                );"""

	db = connect_to_db(db_file_name)
	if db is not None:
		create_table(db, sql_create_fingerprints_table)
        	create_table(db, sql_create_applications_table)
		insert_into_db(db, app_fingerprints)
		db.commit()		
	else:
        	print("Error! Cannot connect to a DB")
	


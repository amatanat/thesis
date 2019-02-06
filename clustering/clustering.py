#!/usr/bin/env python
from __future__ import division
import xml.etree.ElementTree as ET
import sys
import datetime
import json

import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
from sklearn.cluster import KMeans

def total_seconds(time):
	crtime = datetime.datetime.strptime(str(time),'%Y-%m-%dT%H:%M:%SZ')
	epoch = datetime.datetime.strptime("1970-01-01T00:00:00Z",'%Y-%m-%dT%H:%M:%SZ')
	return int((crtime - epoch).total_seconds())

def get_date (seconds):
	date_string = get_date_string(seconds)
	return datetime.datetime.strptime(date_string,'%d-%b-%Y, %H:%M:%S').date()

def get_date_string (seconds):
	return datetime.datetime.fromtimestamp(seconds).strftime('%d-%b-%Y, %H:%M:%S')

def extract_gen_id_and_creation_time (root, inode):
	generation_id_crtime_list = list()
	for fo in root.findall('fileobject'):
		fo_parent_inode = fo.find('parent_object').find('i_node').text
		fo_generation_id = fo.find('genId').text
		fo_crtime = fo.find('crtime')
		
		if (fo_parent_inode is not None and int(fo_parent_inode) == int(inode) and fo_crtime is not None):
			# get total second
			seconds = total_seconds(fo_crtime.text)

			generation_id_crtime_list.append((seconds, fo_generation_id))
	return sorted(generation_id_crtime_list, key=lambda x: x[0])
		
def create_k_means_clusters(data_to_cluster, cluster_count):
	# compute k-means clustering
	kmeans = KMeans(n_clusters = cluster_count).fit(data_to_cluster)
	labels = kmeans.labels_
	#centroids = kmeans.cluster_centers_
	
	for i in range(len(data_to_cluster)):
	    print ("coordinate:", data_to_cluster[i], "label:", labels[i])
	
	return labels

def elbow_criterian(data_to_cluster):
	sse = {}
	for k in range(1, len(data_to_cluster)):
		kmeans = KMeans(n_clusters = k, max_iter = 300).fit(data_to_cluster)
		# Inertia: Sum of squared distances of samples to their closest cluster center
		sse[k] = kmeans.inertia_ 		
	plt.figure()
	plt.plot(list(sse.keys()), list(sse.values()))
	plt.xlabel("Number of cluster")
	plt.ylabel("SSE")
	plt.show()
	cluster_count = input("Please enter cluster count: \n")
	return cluster_count
	
def plot_clusters(X, labels):
	plt.xlabel('timestamp', fontsize = 14)
	plt.ylabel('generation id', fontsize = 14)
	plt.scatter(X[:,0], X[:,1], c = labels, cmap = 'rainbow') 
	plt.show()

def find_wa_db_folder(tree_root, wa_inode):
	# extract genId and creation time of folders
	wa_root_folders = extract_gen_id_and_creation_time(tree_root, wa_inode)
	print wa_root_folders

	output["Installation date"] = get_date_string(wa_root_folders[0][0])

	if len(wa_root_folders) > 2:
		# a user has opened WA after the app installation
		# which means /data/WA/databases folder is created
		# /data/WA/databases folder is in the fifth place in the list 
		wa_db_folder_data = wa_root_folders[4]
		# find an inode of the /data/WA/databases folder using its genID value
		wa_db_folder_inode = find_inode(tree_root, wa_db_folder_data[1]) 

		#output["First time opened WhatsApp after installation"] = get_date_string(wa_root_folders[3][0])

		return wa_db_folder_inode

def find_inode (root, generation_id):
	text = "./fileobject/[genId=" + "'" + str(generation_id) + "'" + "]"
	return root.find(text).find('inode').text

def find_timestamp (root, inode, ts_name):
	text = "./fileobject/[inode=" + "'" + str(inode) + "'" + "]"
	return root.find(text).find(ts_name).text

def find_axolotl_db (root, axolotl_db_data):
	# 1 element in tuple is the generation id of axolotl.db
	axolotl_db_inode = find_inode(root, axolotl_db_data[1])
	
	# append axolotl.db data to output 
	append_to_output("axolotl.db", axolotl_db_inode, 
					 get_date_string(total_seconds(find_timestamp(root, axolotl_db_inode, 'mtime'))),
					 get_date_string(total_seconds(find_timestamp(root, axolotl_db_inode, 'ctime'))),
					 get_date_string(total_seconds(find_timestamp(root, axolotl_db_inode, 'atime'))),
					 get_date_string(total_seconds(find_timestamp(root, axolotl_db_inode, 'crtime'))))

def find_media_db (root, db_files_data):
	# the first 19 files in /data/WA/databases folder are main DB files,
	# created after registration
	# remaining files should be clustered

	data_to_cluster = db_files_data[19:]

	data = np.array(data_to_cluster)
	if len(data_to_cluster) > 4:
		cluster_count = elbow_criterian(data)
	else:
		cluster_count = 1
	
	labels = create_k_means_clusters(data, cluster_count)
	plot_clusters(data, labels)
	
	match_media_db(tree_root, data, labels)

def match_media_db(tree_root, data, labels):
	values = np.array(labels)
	for i in list(set(labels)):
		# array containing index of occurences of i in labels list
		occurences = np.where(values == i)[0]
		# the count of media files is 3, media.db, media.db-wal, media.db-shm
		# if 5 files are created at once then media files are created with the web_session files, 
		# In this case, index 0-1 are web_session files, index 2-4 are media files
		# if 3 files are created at once, then these are media files, index 0-2
		if len(occurences) == 3 or len(occurences) == 5:
			is_len_5 = True if len(occurences) == 5 else False
			
			if is_len_5:
				media_db_inode =  find_inode(tree_root, data[occurences[2]][1])
			else:
				media_db_inode =  find_inode(tree_root, data[occurences[0]][1])

			# extract inode, mtime, atime, ctime, crtime of media.db file and append to output file
			append_to_output("media.db", media_db_inode, 
					 get_date_string(total_seconds(find_timestamp(tree_root, media_db_inode, 'mtime'))),
					 get_date_string(total_seconds(find_timestamp(tree_root, media_db_inode, 'ctime'))),
					 get_date_string(total_seconds(find_timestamp(tree_root, media_db_inode, 'atime'))),
					 get_date_string(total_seconds(find_timestamp(tree_root, media_db_inode, 'crtime'))))

def match_db_folder_files(tree_root, db_folder_inode):
	db_files_genId_and_crtime = extract_gen_id_and_creation_time(tree_root, db_folder_inode)
	
	if len(db_files_genId_and_crtime) > 8:
		# a user has registered
		output["Registration date"] = get_date_string(db_files_genId_and_crtime[8][0])

		# if the crtime of first file in list is today, then we say temporary files are not re-created
		# all files are in the expected order
		if (get_date(db_files_genId_and_crtime[0][0]) == datetime.datetime.today().date()):
			# axolotl.db is in the index 8 in sorted list
			find_axolotl_db(tree_root, db_files_genId_and_crtime[8])

			# if the count of DB files is greater than 19 : media, web_session or emoji dbs are created
			if len (db_files_genId_and_crtime) > 19:
				find_media_db(tree_root, db_files_genId_and_crtime)
		
	else:
		# a user did not register, just installed and opened WA
		output["Info"] = "A user has installed WhatsApp, opened it but did not register."
			

def append_to_output (filename, inode, mtime, ctime, atime, crtime):
	
	data = {
		"inode" : inode,
		"mtime" : mtime,
		"ctime" : ctime, 
		"atime" : atime,
		"crtime": crtime		
		}
	output[filename] = data

def output_result(result):
	with open(output_filename, 'w+') as f:
     		f.write(json.dumps(result))

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python clustering.py <xml_dump_name> </data/WA_inode> <output_filename>"
		exit()

	xml_dump = sys.argv[1]
	wa_inode = int(sys.argv[2])
	output_filename = sys.argv[3] + ".json"	

	tree_root = ET.parse(xml_dump).getroot()
	output = {}

	# get inode of /data/WA/databases folder
	wa_db_folder_inode = find_wa_db_folder(tree_root, wa_inode)

	if wa_db_folder_inode is not None:
		# match files inside /data/WA/databases folder
		match_db_folder_files(tree_root, wa_db_folder_inode)

	output_result(output)
	


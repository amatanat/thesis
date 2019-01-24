#!/usr/bin/env python
from __future__ import division
import xml.etree.ElementTree as ET
import sys
import datetime
from collections import Counter

import matplotlib.pyplot as plt
#import matplotlib as mpl

import numpy as np
from matplotlib import style
from sklearn.cluster import KMeans

def merge_two_dicts(dict_one, dict_two):
    result = dict_one.copy()   
    result.update(dict_two)    
    return result
		
def total_seconds(time):
	crtime = datetime.datetime.strptime(str(time),'%Y-%m-%dT%H:%M:%SZ')
	epoch = datetime.datetime.strptime("1970-01-01T00:00:00Z",'%Y-%m-%dT%H:%M:%SZ')
	return int((crtime - epoch).total_seconds())


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

def find_wa_root_folders(tree_root, wa_inode):
	# extract genId and creation time of folders
	wa_root_folders = extract_gen_id_and_creation_time(tree_root, wa_inode)
	
	# /data/WA/files folder is in third place in the list
	wa_files_folder_data = wa_root_folders[2]
	# find an inode of the /data/WA/files folder using its genID value
	wa_files_folder_inode = find_inode(tree_root, wa_files_folder_data[1])

	# /data/WA/databases folder is in fifth place in the list 
	wa_db_folder_data = wa_root_folders[4]
	# find an inode of the /data/WA/databases folder using its genID value
	wa_db_folder_inode = find_inode(tree_root, wa_db_folder_data[1])

	return (wa_files_folder_inode, wa_db_folder_inode)

def find_inode (root, generation_id):
	text = "./fileobject/[genId=" + "'" + str(generation_id) + "'" + "]"
	return root.find(text).find('inode').text

def match_wam_file(tree_root, files_folder_inode):
	# get generation id and creation time of files inside this folder
	files_gen_id_and_crtime = extract_gen_id_and_creation_time(tree_root, files_folder_inode)
	# this file is created second in the list
	return ("wam.wam", find_inode(tree_root,files_gen_id_and_crtime[1][1]))  

def match_db_folder_files(tree_root, db_folder_inode):
	db_files_genId_and_crtime = extract_gen_id_and_creation_time(tree_root, db_folder_inode)
	print "main db files", db_files_genId_and_crtime
			
	# the first 21 files in /data/WA/databases/ folder are main DB files,
	# created after registration
	# remaining files should be clustered

	data_to_cluster = db_files_genId_and_crtime[21:]

	data = np.array(data_to_cluster)
	if len(data_to_cluster) > 4:
		cluster_count = elbow_criterian(data)
	else:
		cluster_count = 1
	
	labels = create_k_means_clusters(data, cluster_count)
	plot_clusters(data, labels)
	
	media_db_matching = match_media_db(tree_root, data, labels)
	wa_db_matching = match_wa_db(tree_root, db_files_genId_and_crtime[:11])
	# media database files are available
	if media_db_matching is not None:
		return merge_two_dicts(media_db_matching, wa_db_matching)
	else: 
		return wa_db_matching

def match_wa_db(tree_root, data):
	matching = {}
	matching["wa.db"] = find_inode(tree_root, data[7][1])
	matching["wa.db-wal"] = find_inode(tree_root, data[8][1])
	matching["wa.db-shm"] = find_inode(tree_root, data[9][1])
	return matching	

def match_media_db(tree_root, data, labels):
	matching = {}
	values = np.array(labels)
	for i in list(set(labels)):
		# array containing index of occurences of i in labels list
		occurences = np.where(values == i)[0]
		# the count of media files is 3
		if len(occurences) == 3:
			matching["media.db"] = find_inode(tree_root, data[occurences[0]][1])
			matching["media.db-wal"] = find_inode(tree_root, data[occurences[1]][1])
			matching["media.db-shm"] = find_inode(tree_root, data[occurences[2]][1])
			return matching
			
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: python clustering.py <xml_dump_name> <WA_inode>"
		exit()

	xml_dump = sys.argv[1]
	wa_inode = int(sys.argv[2])
	
	tree_root = ET.parse(xml_dump).getroot()

	# get inode of /data/WA/files and /data/WA/databases folders
	wa_root_folder_inodes = find_wa_root_folders(tree_root, wa_inode)

	# identify files inside /data/WA/files folder
	files_folder_match = match_wam_file(tree_root, wa_root_folder_inodes[0])
	print files_folder_match

	# match files inside /data/WA/databases folder
	db_folder_match = match_db_folder_files(tree_root, wa_root_folder_inodes[1])
	print db_folder_match
	


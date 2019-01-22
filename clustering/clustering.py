#!/usr/bin/env python
from __future__ import division
import xml.etree.ElementTree as ET
import sys
import datetime

import matplotlib.pyplot as plt
#import matplotlib as mpl

import numpy as np
from matplotlib import style
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
		

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
		
		if (fo_parent_inode is not None and int(fo_parent_inode) == inode and fo_crtime is not None):
			# get total second
			seconds = total_seconds(fo_crtime.text)

			generation_id_crtime_list.append((seconds, fo_generation_id))
	return generation_id_crtime_list
		
def create_k_means_clusters(data_to_cluster):
	# number of clusters to create
	kmeans = KMeans(n_clusters = 3).fit(data_to_cluster)
	labels = kmeans.labels_
	#centroids = kmeans.cluster_centers_
	#print centroids
	#print labels
	
	for i in range(len(data_to_cluster)):
	    print ("coordinate:", data_to_cluster[i], "label:", labels[i])
	
	return labels


def elbow_criterian(data_to_cluster):
	sse = {}
	for k in range(1, 10):
	    kmeans = KMeans(n_clusters = k, max_iter = 1000).fit(data_to_cluster)
	# Inertia: Sum of distances of samples to their closest cluster center
	    sse[k] = kmeans.inertia_ 
	plt.figure()
	plt.plot(list(sse.keys()), list(sse.values()))
	plt.xlabel("Number of cluster")
	plt.ylabel("SSE")
	plt.show()
	
def plot_clusters(X, labels):
	plt.xlabel('timestamps', fontsize=14)
	plt.ylabel('generation id', fontsize=14)
	plt.scatter(X[:,0],X[:,1], c=labels, cmap='rainbow') 
	plt.show()


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: python node.py <xml_dump_name> <database_inode>"
		exit()

	xml_dump = sys.argv[1]
	db_inode = int(sys.argv[2])
	
	tree_root = ET.parse(xml_dump).getroot()
	files_generation_id_crtime = extract_gen_id_and_creation_time(tree_root, db_inode)
	# sort a list by crtime
	sorted([files_generation_id_crtime], key=lambda x: x[0])
	
	# the first 21 files belong to the first cluster
	# we need to cluster the rest files
	data_to_cluster = files_generation_id_crtime[21:]

	data = np.array(data_to_cluster)
	
	elbow_criterian(data)
	labels = create_k_means_clusters(data)
	plot_clusters(data, labels)
	



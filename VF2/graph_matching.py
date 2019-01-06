#!/usr/bin/env python
from __future__ import division
import xml.etree.ElementTree as ET
import sys
import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt
import matplotlib as mpl

def node_matching(node_a, node_b):
	if node_a['type'] == node_b['type']:
		print "types are equal"
		if node_a['filesize'] is None and node_b['filesize'] is None:
			print "size is none"
			return True
		if node_a['filesize'] is None or node_b['filesize'] is None:
			print "one is none"
			return False 
		size_percentage_difference = calculate_percentage_difference(node_a['filesize'], node_b['filesize'])
		order_percentage_difference = calculate_percentage_difference(node_a['size_order'], node_b['size_order'])
		if size_percentage_difference < size_threshold and order_percentage_difference < size_order_threshold:
			print size_percentage_difference, order_percentage_difference
			return True
	return False
	
def calculate_percentage_difference (a,b):
	if a == 0 and b == 0:
		return 0
	return int((abs(a - b) * 100) / ((a + b) / 2))

def subgraph_isomorphism (G1, G2) :
	digraph_matcher = isomorphism.DiGraphMatcher(G2,G1,node_match=node_matching)
	for subgraph in digraph_matcher.subgraph_isomorphisms_iter():
    		print subgraph
	print "G2 is subgraph isomorphic G1:" , str(digraph_matcher.subgraph_is_isomorphic())
	print "G2 - G1 mapping:" , str(digraph_matcher.mapping)

def initialize_graph(edges, nodes):
	G = nx.DiGraph()
	for node in nodes:
		G.add_node(node[0], filesize=node[1])	
		G.nodes[node[0]]['type'] = str(node[2])
		G.nodes[node[0]]['size_order'] = int(node[3])

	G.add_edges_from(edges)
		
	pos = nx.layout.kamada_kawai_layout(G)
	node_sizes = [10 + 10 * i for i in range(len(G))]
	nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
	edgess = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
                               arrowsize=10, edge_color="orange",
                              edge_cmap=plt.cm.Blues, width=2)

	#pc = mpl.collections.PatchCollection(edgess, cmap=plt.cm.Blues)
	ax = plt.gca()
	ax.set_axis_off()
	plt.show()
	
	#print G.nodes()
	#print G.edges()
	return G

def find_app_inode (root,filename):
	text = "./fileobject/[filename=" + "'" + str(filename) + "'" + "]"
	return root.find(text).find('inode').text

def find_size(root,inode):
	text = "./fileobject/[inode=" + "'" + str(inode) + "'" + "]"
	return int(root.find(text).find('filesize').text)

def find_size_order (root, parent_inode, file_inode):
	"""Create a list containing (inode,size) tuple of files in a given folder. 
	Return size_order of a requested file."""
	inode_size_list = list()
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_name_type = fileobject.find('name_type').text 
		fo_inode = fileobject.find('inode')
		fo_filesize = fileobject.find('filesize')

		if (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and 
			str(fo_name_type) == str("r/r") and fo_inode is not None and fo_filesize is not None and
			fo_inode.text is not None and fo_filesize.text is not None):

			inode_size_list.append((int(fo_inode.text),int(fo_filesize.text)))

		elif (fo_parent_inode is not None and int(fo_parent_inode) == int(parent_inode) and
			str(fo_name_type) == str("r/r") and fo_inode is not None and fo_filesize is not None and
			fo_inode.text is not None and fo_filesize.text is None):

			inode_size_list.append((int(fo_inode.text), 0))

	# sort a list by a second value in tuples, i.e by size
	sorted_list = sorted(inode_size_list, key=lambda tup: tup[1])
	
	return [t[0] for t in sorted_list].index(int(file_inode))

def extract_nodes_and_edges (root, inode, nodes_list, edges_list, is_fde):
	for fileobject in root.findall('fileobject'):
		fo_parent_inode = fileobject.find('parent_object').find('i_node').text
		fo_inode =  fileobject.find('inode').text
		fo_size = fileobject.find('filesize').text
		fo_type = fileobject.find('name_type').text
		
		if is_fde:
			fo_name = fileobject.find('filename').text
			if (fo_parent_inode is not None and int(fo_parent_inode) == inode and 
				fo_name is not None and fo_inode is not None and 
				not str(fo_name).startswith(tuple(prefixes))): 

				print fo_name
				append_to_list(root, inode, fo_inode, fo_type, fo_size, nodes_list, edges_list,)
				extract_nodes_and_edges(root, int(fo_inode), nodes_list, edges_list, is_fde)
		
		elif (fo_parent_inode is not None and int(fo_parent_inode) == inode and 
					fo_inode is not None):

			append_to_list(root, inode, fo_inode, fo_type, fo_size, nodes_list, edges_list,)
			extract_nodes_and_edges(root, int(fo_inode), nodes_list, edges_list, is_fde)
			
def append_to_list(root, inode, fo_inode, fo_type, fo_size, nodes_list, edges_list) :
	size_order = 0 if str(fo_type) == "d/d" else find_size_order(root, inode, fo_inode)
	if fo_size is None:
		nodes_list.append((int(fo_inode), fo_size, fo_type, size_order))
	else:
		nodes_list.append((int(fo_inode), int(fo_size), fo_type, size_order))
	edges_list.append((int(inode), int(fo_inode)))

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python node.py <xml_dump_name_fde> <xml_dump_name_fbe> <data_whatsapp_inode> <size_threshold> <size_order_threshold>"
		exit()

	fde_xml_dump = sys.argv[1]
	fbe_xml_dump = sys.argv[2]
	fbe_data_whatsapp_inode = int(sys.argv[3])
        size_threshold = int(sys.argv[4])
        size_order_threshold = int(sys.argv[5])

	fde_nodes = list()
	fde_edges = list()

	fbe_nodes = list()
	fbe_edges = list()
	
	fde_root = ET.parse(fde_xml_dump).getroot()
	fbe_root = ET.parse(fbe_xml_dump).getroot()

	fde_data_whatsapp_inode = int(find_app_inode(fde_root ,"data/com.whatsapp"))
	fde_data_whatsapp_filesize = int(find_size(fde_root, fde_data_whatsapp_inode))
	fde_nodes.append( (int(fde_data_whatsapp_inode), fde_data_whatsapp_filesize,"d/d",0) )

	fbe_data_whatsapp_filesize = int(find_size(fbe_root, fbe_data_whatsapp_inode))
	fbe_nodes.append((fbe_data_whatsapp_inode, fbe_data_whatsapp_filesize,"d/d",0))

	prefixes = ["data/com.whatsapp/files/Logs", "data/com.whatsapp/files/key",
			"data/com.whatsapp/files/statistics", "data/com.whatsapp/files/me",
			"data/com.whatsapp/files/rc2", "data/com.whatsapp/files/login_failed",
			"data/com.whatsapp/files/downloadable", "data/com.whatsapp/files/Avatars", 
			"data/com.whatsapp/files/.trash", "data/com.whatsapp/files/invalid_numbers",
                	"data/com.whatsapp/shared_prefs", "data/com.whatsapp/no_backup", "data/com.whatsapp/code_cache",
			"data/com.whatsapp/cache", "data/com.whatsapp/app_minidumps", "data/com.whatsapp/app_traces",
			"data/com.whatsapp/files/emoji", 
			"data/com.whatsapp/files/Stickers",
			"data/com.whatsapp/databases/web_sessions",
			"data/com.whatsapp/databases/msgstore",
			"data/com.whatsapp/databases/chatsettings",
			"data/com.whatsapp/databases/axolotl",
			"data/com.whatsapp/databases/location",
			#"data/com.whatsapp/databases/media.db",
			#"data/com.whatsapp/databases/wa.db",
			"data/com.whatsapp/databases/_jobqueue",
			"data/com.whatsapp/databases/emojidictionary", 
			"data/com.whatsapp/databases/hsmpacks"]

	extract_nodes_and_edges(fde_root, fde_data_whatsapp_inode, fde_nodes, fde_edges, True)
	extract_nodes_and_edges(fbe_root, fbe_data_whatsapp_inode, fbe_nodes, fbe_edges, False)

	FDE_G = initialize_graph(fde_edges, fde_nodes)
	FBE_G = initialize_graph(fbe_edges, fbe_nodes)
	
	subgraph_isomorphism(FDE_G,FBE_G)
	



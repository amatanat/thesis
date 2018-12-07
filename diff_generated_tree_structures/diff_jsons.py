#!/usr/bin/env python

import sys
import json

def append_to_output (key, data):
	output[key].append(data)	

def compare_dictionaries (dict1, dict2):
	""" compare 2 dictionaries and return a list of 
	keys having different values"""
	result = list()
	for key in dict1.keys():
		if dict1[key] != dict2[key]:
			result.append(key)
	return result

def compare (data_before_action, data_after_action):
	new_file = True
	for data_ba in data_before_action:
		for data_ac in data_after_action:
			if (data_ac['depth'] == data_ba['depth'] and 
				data_ac['name_size'] == data_ba['name_size'] and 
				data_ac['mode'] == data_ba['mode']):
					# compare file's data before and after an action
					result = compare_dictionaries(data_ba, data_ac)
					# add file's data and comparison result to output
					append_to_output('Changed', (data_ac, result))

					# delete already processed file's data
					del data_after_action[data_after_action.index(data_ac)]

					new_file = False
					break
		if new_file:	
			# data is not present in data_after_action,
			# which means this file is deleted	
			append_to_output('Deleted files', data_ba)
		else:
			new_file = True
	
	# data present in data_before_action and not in data_after_action are deleted data
	if len(data_after_action) > 0:
		for item in data_after_action:
			append_to_output('New files', item)

def output_json(filename) :
	with open(filename, 'w+') as outfile:
    		json.dump(output, outfile)

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Usage: python diff_json.py <1_json_filename> <2_json_filename> <output_filename>"
		exit()

	dump1 = sys.argv[1] 
	dump2 = sys.argv[2] 
	output_filename = sys.argv[3]

	with open(dump1, "r") as f:
  			data_ba = json.loads(f.read())

	with open(dump2, "r") as f:
  			data_ac = json.loads(f.read())

	output = {}
	output['New files'] = list()
	output['Deleted files'] = list()
	output['Changed'] = list()

	compare(data_ba, data_ac)
	output_json(output_filename + ".json")





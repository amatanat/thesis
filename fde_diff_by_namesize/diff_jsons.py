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
	for data_ba in data_before_action:
		for data_ac in data_after_action:
			if (data_ac['depth'] == data_ba['depth'] and data_ac['name_size'] == data_ba['name_size']):
				# compare file's data before and after an action
				result = compare_dictionaries(data_ba, data_ac)

				# add file's data and comparison result to output
				if len(result) > 0:
					append_to_output('Changed', (data_ac, result))

				# delete already processed file's data
				del data_after_action[data_after_action.index(data_ac)]
				break

def output_json (filename) :
	with open(filename, 'w+') as outfile:
    		json.dump(output, outfile)

def find_unique_name_size (data):
	"""Find files those having unique 'name_size' in the same depth"""
	result = list()
	for item in data:
		count = sum([1 for i in data if item["name_size"] == i["name_size"] and item["depth"] == i["depth"]])
		if count == 1:
			print item["depth"], item["name_size"], item["filename"]
			result.append(item)
	return result

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
	output['Changed'] = list()

	ba_unique_name_size = find_unique_name_size(data_ba)
	ac_unique_name_size = find_unique_name_size(data_ac)

	compare(ba_unique_name_size, ac_unique_name_size)
	output_json(output_filename + ".json")





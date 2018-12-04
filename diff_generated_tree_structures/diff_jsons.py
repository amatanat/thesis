#!/usr/bin/env python

import sys
import json


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
  			data1 = json.loads(f.read())

	with open(dump2, "r") as f:
  			data2 = json.loads(f.read())

	output = []
	[[output.append((y, k)) for k in x if x[k] != y[k]] for i, (x, y) in enumerate(zip(data1,data2)) if x != y]
	output_json(output_filename + ".json")

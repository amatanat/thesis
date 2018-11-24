#!/usr/bin/env python

import sys
import json

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python diff_json.py <1_json_filename> <2_json_filename>"
		exit()

	dump1 = sys.argv[1] 
	dump2 = sys.argv[2] 

	with open(dump1, "r") as f:
  			data1 = json.loads(f.read())

	with open(dump2, "r") as f:
  			data2 = json.loads(f.read())

	a_set = { frozenset(j.items()) for i in data1.values() for j in i }
	b_set = { frozenset(k.items()) for v in data2.values() for k in v }
	print (a_set - b_set)
	

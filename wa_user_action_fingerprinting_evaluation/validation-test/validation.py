#!/usr/bin/env python 
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
import json

def is_correct_match (action_name):
	for match in root.findall('match'):
		found_action = match.find('action_name').text
		if found_action == action_name:
			output.append(("correct action_name match: " , action_name, "action run count:" , run_count ))
			return
	output.append(("could not match: ", action_name, "action run count:", run_count))

def validate_identified_actions (root, first_action, second_action):
	text_action_name_list = ['CSM', 'FM', 'RM', 'PN-text']
	photo_action_name_list = ['CSP', 'FP', 'RP', 'PN']

	if first_action in text_action_name_list:
		if second_action in photo_action_name_list:
			is_correct_match('send_or_receive_photo')	
		else:
			is_correct_match('send_or_receive_text')

	if first_action in photo_action_name_list:
		if second_action in text_action_name_list:
			is_correct_match('send_or_receive_text')
			is_correct_match('send_or_receive_photo')

 		else:
			is_correct_match('send_or_receive_photo')

def total_seconds(date_time):
	date_time = datetime.strptime(str(date_time),'%d-%b-%Y, %H:%M:%S')
	epoch = datetime.strptime("01-Jan-1970, 00:00:00",'%d-%b-%Y, %H:%M:%S')
	return int((date_time - epoch).total_seconds())

def get_action_datetime_in_seconds (required_text):
	for line in reversed(open(log_filename).readlines()):
		if required_text in line:    
			line = line.rstrip().split()		
			action_date = line[0]
			action_time = line[1]
			action_datetime = action_date + " " + action_time
			return total_seconds(datetime.strptime(action_datetime, '%Y-%m-%d %H:%M:%S').strftime('%d-%b-%Y, %H:%M:%S'))
	return None

def find_offset (element, timestamp_name, action_datetime_in_seconds, result, found_action):
	for ts in element:
		if ts.tag == 'filename':
			result[found_action][timestamp_name].append(('filename', ts.text))
		if ts.tag == 'date':
			result[found_action][timestamp_name].append(('offset', total_seconds(ts.text) - action_datetime_in_seconds))
	return result


def evaluate_timestamps (match, action_datetime_in_seconds, found_action):
	result = dict()
	result[found_action] = dict()
	result[found_action]['correct_timestamp'] = list()
	result[found_action]['wrong_timestamp'] = list()

	for elem in match.iter():

		if elem.tag == 'correct_timestamp':
			result = find_offset(elem, 'correct_timestamp', action_datetime_in_seconds, result, found_action)

		if elem.tag == 'wrong_timestamp':
			result = find_offset(elem, 'wrong_timestamp', action_datetime_in_seconds, result, found_action)
	return result

def validate_action_time (root, first_action, second_action):
	for match in root.findall('match'):
		found_action = match.find('action_name').text

		if found_action == 'send_or_receive_text':
			# extract datetime corresponding to 'type message' from log file
			type_message_in_seconds = get_action_datetime_in_seconds("type message")
			if type_message_in_seconds is not None:
				output.append(evaluate_timestamps(match, type_message_in_seconds, found_action))

		if found_action == 'send_or_receive_photo':
			# extract datetime corresponding to 'select photo' from log file
			select_photo_in_seconds = get_action_datetime_in_seconds("select photo")
			if select_photo_in_seconds is not None:
				output.append(evaluate_timestamps(match, select_photo_in_seconds, found_action))

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print "Usage: python validation.py <identified_actions_xml> <log_filename> <action_name_1> <action_name_2> <run_count>"
		exit()

	identified_actions_xml = sys.argv[1] 
	log_filename = sys.argv[2] 
	first_action = sys.argv[3]
	second_action = sys.argv[4]
	run_count = sys.argv[5]

	output = list()

	root = ET.parse(identified_actions_xml).getroot()

	validate_identified_actions (root, first_action, second_action)

	validate_action_time (root, first_action, second_action)

	with open(first_action + "-" + second_action + "-output.json", 'a') as f:
     		f.write(json.dumps(output, indent=4))



#!/usr/bin/env python 
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

def is_correct_match (action_name):
	for match in root.findall('match'):
		found_action = match.find('action_name').text
		if found_action == action_name:
			print "correct action_name match, " , action_name, run_count
			return
	print "could not match, ", action_name, run_count

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

def is_in_range (num_1, num_2, found_action_datetime_in_seconds, threshold):
	# determine whether or not found action time corresponds to the actual action time 
	return num_1 <= found_action_datetime_in_seconds <= num_2 + threshold

def validate_action_time (root, threshold):
	for match in root.findall('match'):
		found_action = match.find('action_name').text
		date_time = match.find('date').text
		found_action_datetime_in_seconds = total_seconds(date_time)
		if found_action == 'send_or_receive_text':
			# extract datetime corresponding to 'type message' and 'send message' from log file
			type_message_in_seconds = get_action_datetime_in_seconds("type message")
			send_message_in_seconds = get_action_datetime_in_seconds("send message")

			if (type_message_in_seconds is not None and send_message_in_seconds is not None
				and is_in_range(type_message_in_seconds, 
						send_message_in_seconds, 
						found_action_datetime_in_seconds, 
						threshold)):
					print "correct time for send_or_receive_text", run_count

		if found_action == 'send_or_receive_photo':
			# extract datetime corresponding to 'select photo' and 'click send button' from log file
			select_photo_in_seconds = get_action_datetime_in_seconds("select photo")
			send_photo_in_seconds = get_action_datetime_in_seconds("click send button")

			if (select_photo_in_seconds is not None and send_photo_in_seconds is not None
				and is_in_range(select_photo_in_seconds, 
						send_photo_in_seconds, 
						found_action_datetime_in_seconds, 
						threshold)):
					print "correct time for send_or_receive_photo", run_count

if __name__ == '__main__':
	if len(sys.argv) < 6:
		print "Usage: python validation.py <identified_actions_xml> <log_filename> <threshold> <action_name_1> <action_name_2> <run_count>"
		exit()

	identified_actions_xml = sys.argv[1] 
	log_filename = sys.argv[2] 
	threshold = int(sys.argv[3])
	first_action = sys.argv[4]
	second_action = sys.argv[5]
	run_count = sys.argv[6]

	root = ET.parse(identified_actions_xml).getroot()

	validate_identified_actions (root, first_action, second_action)

	validate_action_time (root, threshold)



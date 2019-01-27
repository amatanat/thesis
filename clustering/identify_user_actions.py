import sys
import json
from datetime import datetime

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom

#constants
SEND_PHOTO_FILES = ["wam.wam", "media.db", "media.db-wal", "media.db-shm"]
RECEIVE_PHOTO_FILES = ["wa.db-wal", "media.db", "media.db-wal", "media.db-shm"]
SEND_TEXT_FILES =  ["wam.wam"]
RECEIVE_TEXT_FILES = ["wa.db-wal"]
WAM_FILE = "wam.wam"
WA_WAL_FILE = "wa.db-wal"
MEDIA_DB_FILE = "media.db"
MEDIA_WAL_FILE = "media.db-wal"
MEDIA_SHM_FILE = "media.db-shm"
C_TIME = "ctime"
M_TIME = "mtime"
CR_TIME = "crtime"
SEND_PHOTO = "SEND_PHOTO"
RECEIVE_PHOTO = "RECEIVE_PHOTO"
RECEIVE_TEXT = "RECEIVE_TEXT"
SEND_TEXT = "SEND_TEXT"
SEND_TEXT_OR_PHOTO = "SEND_TEXT_OR_PHOTO"
RECEIVE_TEXT_OR_PHOTO = "RECEIVE_TEXT_OR_PHOTO"
SEND_OR_RECEIVE_PHOTO = "SEND_OR_RECEIVE_PHOTO"


def is_timestamp_changed (data, filename):
	"""Return True if mtime or ctime of a file has changed. Otherwise return False"""
	if data[filename][CR_TIME] != data[filename][M_TIME] or data[filename][CR_TIME] != data[filename][C_TIME]:
		return True
	return False

def total_seconds (time):
	"""Convert input time to seconds since epoch"""
	input_time = datetime.strptime(str(time),'%Y-%m-%dT%H:%M:%SZ')
	epoch = datetime.strptime("1970-01-01T00:00:00Z",'%Y-%m-%dT%H:%M:%SZ')
	return int((input_time - epoch).total_seconds())

def passes_threshold (media_one, media_two, media_tree, time_four):
	"""The first three input files are media files, the fourth is either WAM_FILE or WA_WAL_FILE
	Convert input times to seconds. Find the max value of media files and subtract the value of the fourth file. 
	Return True if the value is less than given threshold, otherwise return False""" 
	return abs(max(total_seconds(media_one), total_seconds(media_two), total_seconds(media_tree)) - 
		total_seconds(time_four)) < threshold

def is_file_available (data, filename):
	"""Return True is the given file is available in the input data file, otherwise return False"""
	return True if filename in data else False

def find_accuracy (data, files, total_count):
	"""data is the input data file. files is a list of file names. 
	total_count - total count of files that should change its timestamps.""" 
	file_name_and_ts = {}
	correct_ts = {}
	wrong_ts = {}
	for file_name in files:
		file_name_and_ts[file_name] = total_seconds(data[file_name][C_TIME])

	max_ts = max([ts for ts in file_name_and_ts.values()]) 

	# count of the changed timestamps
	changed_ts = 0

	for file_name, ts in file_name_and_ts.items():
		# if the max timestamp minus timestamp is less that given threshold then 
		# timestamp has changed.
		if max_ts - ts < threshold:
			if file_name == MEDIA_DB_FILE:
				# MEDIA_DB_FILE only changes its ctime
				# increment count by 1 for the ctime change
				changed_ts += 1
				correct_ts[file_name] = C_TIME
			else:
				# all other files change mtime and ctime. 
				# if ctime has changed then mtime of these files has also changed.
				# increment count by 2, one for ctime and one for mtime change.
				changed_ts += 2
				correct_ts[file_name] = (C_TIME ,M_TIME)
		else:
			if file_name == MEDIA_DB_FILE:		
				wrong_ts[file_name] = C_TIME
			else:
				wrong_ts[file_name] = (C_TIME ,M_TIME)

	accuracy_perc = (changed_ts * 100) / total_count
	return (correct_ts, wrong_ts, accuracy_perc, changed_ts)

def find_actions (data):
	result = list()

	is_send_photo = False
	is_receive_photo = False

	is_media_available = is_file_available(data, MEDIA_DB_FILE)
	is_wa_wal_available = is_file_available(data, WA_WAL_FILE)
	is_wam_changed = is_timestamp_changed(data, WAM_FILE)

	if is_media_available and is_wam_changed:
		# media files and WAM_FILE changed at the same time, which is a send-photo action
		if passes_threshold(data[MEDIA_DB_FILE][C_TIME], data[MEDIA_WAL_FILE][C_TIME], 
				data[MEDIA_SHM_FILE][C_TIME], data[WAM_FILE][C_TIME]):
			accuracy = find_accuracy(data, SEND_PHOTO_FILES, 7)
			result.append((SEND_PHOTO, data[MEDIA_WAL_FILE][C_TIME], accuracy[2], accuracy[0], accuracy[1], accuracy[3],7))
			is_send_photo = True

	if is_media_available and is_wa_wal_available:
		# media files and WA_WAL_FILE changed at the same time, which is a receive-photo action
		if passes_threshold(data[MEDIA_DB_FILE][C_TIME], data[MEDIA_WAL_FILE][C_TIME], 
				data[MEDIA_SHM_FILE][C_TIME], data[WA_WAL_FILE][C_TIME]):
			accuracy = find_accuracy(data, RECEIVE_PHOTO_FILES, 7)
			result.append((RECEIVE_PHOTO, data[MEDIA_WAL_FILE][C_TIME], accuracy[2], accuracy[0], accuracy[1], accuracy[3],7))
			is_receive_photo = True
			
	if is_wam_changed:
		accuracy = find_accuracy(data, SEND_TEXT_FILES, 2)
		# WAM_FILE changed and a receive-photo action happened
		if not is_send_photo and is_receive_photo:
			# after receiving a media, a new text message was send 
			if total_seconds(data[MEDIA_WAL_FILE][C_TIME]) < total_seconds(data[WAM_FILE][C_TIME]):
				result.append((SEND_TEXT, data[WAM_FILE][C_TIME], accuracy[2], accuracy[0], accuracy[1], accuracy[3],2))	
			else:
			# before receiving media, text or media was send.
				accuracy = find_accuracy(data, SEND_PHOTO_FILES, 7)
				result.append((SEND_TEXT_OR_PHOTO, data[WAM_FILE][C_TIME], accuracy[2],accuracy[0],accuracy[1], accuracy[3],7))
		# neither send-photo nor receive-photo actions happened, but WAM_FILE was changed
		elif not is_send_photo and not is_receive_photo :
			result.append((SEND_TEXT, data[WAM_FILE][C_TIME], accuracy[2], accuracy[0], accuracy[1], accuracy[3],2))	

	if is_wa_wal_available:
		accuracy = find_accuracy(data, RECEIVE_TEXT_FILES, 2)
		# WA_WAL_FILE changed and send-photo action happened
		if not is_receive_photo and is_send_photo:
			# after sending media, a new text message was received
			if total_seconds(data[MEDIA_WAL_FILE][C_TIME]) < total_seconds(data[WA_WAL_FILE][C_TIME]):
				result.append((RECEIVE_TEXT, data[WA_WAL_FILE][C_TIME],  accuracy[2], accuracy[0], accuracy[1], accuracy[3],2))	
			else:
			# before sending media, text or media was received
				accuracy = find_accuracy(data, RECEIVE_PHOTO_FILES, 7)
				result.append((RECEIVE_TEXT_OR_PHOTO, data[WA_WAL_FILE][C_TIME],  accuracy[2], accuracy[0], accuracy[1], accuracy[3],7))
		# neither send-photo not receive-photo actions happened, but WA_WAL_FILE was changed
		elif not is_receive_photo and not is_send_photo:
			result.append((RECEIVE_TEXT, data[WA_WAL_FILE][C_TIME],  accuracy[2], accuracy[0], accuracy[1], accuracy[3],2))		

	if not is_send_photo and not is_receive_photo and is_media_available:	
		# neither send_photo nor receive_photo actions happend, but media file was created
		# which means after media creation (in send or receive), text was send or received. 
		accuracy = find_accuracy(data, RECEIVE_PHOTO_FILES, 7)
		result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_WAL_FILE][C_TIME], accuracy[2], accuracy[0], accuracy[1], accuracy[3],7))

	return result

def generate_XML(result, output_filename):
	comment = Comment('List of found actions')
	top = Element('xml')
	top.append(comment)
	create_match_tag(top, result)
	save_to_xml(output_filename + ".xml", top)

def save_to_xml(output_filename, top):
	root = tostring(ET.ElementTree(top).getroot())
	xml_str = minidom.parseString(root).toprettyxml(indent="   ")
	with open(output_filename, "w") as f:
		f.write(xml_str)

def create_timestamp_tag(parent, child_tag_name, key, value):
	child_tag = SubElement(parent, child_tag_name)
	file_name = SubElement(child_tag, 'filename')
	file_name.text = key
	timestamps = SubElement(child_tag, 'timestamps')
	timestamps.text = str(value)

def convert_time_to_readable_format(date_string):
	date_time = datetime.strptime(date_string,'%Y-%m-%dT%H:%M:%SZ')
	return date_time.strftime('%d-%b-%Y, %H:%M:%S' )

def create_match_tag(top, result):
	for action in result:
		match = SubElement(top, 'match')
		action_name = SubElement(match, 'action_name')
		action_name.text = action[0]
		action_date = SubElement(match, 'date')
		action_date.text = convert_time_to_readable_format(str(action[1]))
		accuracy = SubElement(match, 'accuracy')
		percentage = SubElement(accuracy, 'percentage')
		percentage.text = str(action[2])
		timestamps = SubElement(accuracy, 'timestamps')
		timestamps.text = str(action[5]) + "/" + str(action[6])
		correct_timestamps = SubElement(accuracy, 'correct_timestamps')
		
		for key, value in action[3].items():
			create_timestamp_tag(correct_timestamps, 'correct_timestamp', key, value)
		
		wrong_timestamps = SubElement(accuracy, 'wrong_timestamps')
		for key, value in action[4].items():
			create_timestamp_tag(wrong_timestamps, 'wrong_timestamp', key, value)
		

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Usage: python identify_user_actions.py <clustering_generated_output> <threshold_in_seconds> <output_filename>"
		exit()

	input_data = sys.argv[1] 
	threshold = int(sys.argv[2])
	output_filename = sys.argv[3] 

	with open(input_data, "r") as f:
  			data = json.loads(f.read())
			actions = find_actions(data)
			generate_XML(actions, output_filename)
	

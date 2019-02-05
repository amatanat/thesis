import sys
import json
from datetime import datetime

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom

#constants
SEND_OR_RECEIVE_PHOTO_FILES = ["axolotl.db", "media.db"]
SEND_OR_RECEIVE_TEXT_FILES = ["axolotl.db"]
MEDIA_DB_FILE = "media.db"
AXOLOTL_DB_FILE = "axolotl.db"
C_TIME = "ctime"
M_TIME = "mtime"
SEND_OR_RECEIVE_PHOTO = "send_or_receive_photo"
SEND_OR_RECEIVE_TEXT = "send_or_receive_text"


def total_seconds (time):
	"""Convert input time to seconds since epoch"""
	input_time = datetime.strptime(str(time),'%Y-%m-%dT%H:%M:%SZ')
	epoch = datetime.strptime("1970-01-01T00:00:00Z",'%Y-%m-%dT%H:%M:%SZ')
	return int((input_time - epoch).total_seconds())

def passes_threshold (time_one, time_two):
	return abs(total_seconds(time_one) - total_seconds(time_two)) < threshold

def is_file_available (data, filename):
	"""Return True is the given file is available in the input data file, otherwise return False"""
	return True if filename in data else False

#TODO do we need to calculate accuracy?
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
			changed_ts += 1
			correct_ts[file_name] = (C_TIME, data[file_name][C_TIME])
		else:
			wrong_ts[file_name] = (C_TIME, data[file_name][C_TIME])

	accuracy_perc = (changed_ts * 100) / total_count
	return ( accuracy_perc, changed_ts, correct_ts, wrong_ts)

def is_user_action (db_ctime, db_mtime):
	# in user action ctime of db file is different from mtime of db file
	return abs(total_seconds(db_ctime) - total_seconds(db_mtime)) > 2

def find_actions (data):
	result = list()

	is_axolotl_available = is_file_available(data, AXOLOTL_DB_FILE)
	is_media_available = is_file_available(data, MEDIA_DB_FILE)

	axolotl_changed = False
	media_changed = False

	if is_axolotl_available:
		axolotl_changed = is_user_action(data[AXOLOTL_DB_FILE][C_TIME], data[AXOLOTL_DB_FILE][M_TIME])

	if is_media_available:
		media_changed = is_user_action(data[MEDIA_DB_FILE][C_TIME], data[MEDIA_DB_FILE][M_TIME])

	if axolotl_changed:
		if media_changed:
			if passes_threshold(data[AXOLOTL_DB_FILE][C_TIME], data[MEDIA_DB_FILE][C_TIME]):
				result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME]))
			else:
				result.append((SEND_OR_RECEIVE_TEXT, data[AXOLOTL_DB_FILE][C_TIME]))
				result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME]))
		else:
			result.append((SEND_OR_RECEIVE_TEXT, data[AXOLOTL_DB_FILE][C_TIME]))

	elif media_changed:
		result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME]))
	return result

def generate_XML(result, output_filename, input_data):
	top = Element('xml')
	create_info_tag(top, input_data)
	create_match_tag(top, result)
	save_to_xml(output_filename + ".xml", top)

def save_to_xml (output_filename, top):
	root = tostring(ET.ElementTree(top).getroot())
	xml_str = minidom.parseString(root).toprettyxml(indent="   ")
	with open(output_filename, "w") as f:
		f.write(xml_str)

def create_timestamp_tag (parent, child_tag_name, key, value):
	child_tag = SubElement(parent, child_tag_name)
	file_name = SubElement(child_tag, 'filename')
	file_name.text = key
	timestamps = SubElement(child_tag, 'timestamps')
	timestamps.text = str(value)

def convert_time_to_readable_format (date_string):
	date_time = datetime.strptime(date_string,'%Y-%m-%dT%H:%M:%SZ')
	return date_time.strftime('%d-%b-%Y, %H:%M:%S')

def create_info_tag (top, input_data):
	info = SubElement(top, 'info')
	if "Installation date" in input_data:
		installation_date = SubElement(info, 'app_installation_date')
		installation_date.text = input_data["Installation date"]

	if "Registration date" in input_data:
		registration_date = SubElement(info, 'app_registration_date')
		registration_date.text = input_data["Registration date"]

def create_match_tag (top, result):
	for action in result:
		match = SubElement(top, 'match')
		action_name = SubElement(match, 'action_name')
		action_name.text = action[0]
		action_date = SubElement(match, 'date')
		action_date.text = convert_time_to_readable_format(str(action[1]))
		#accuracy = SubElement(match, 'accuracy')
		#percentage = SubElement(accuracy, 'percentage')
		#percentage.text = str(action[2])
		#timestamps = SubElement(accuracy, 'timestamps')
		#timestamps.text = str(action[5]) + "/" + str(action[6])
		#correct_timestamps = SubElement(accuracy, 'correct_timestamps')
		
		#for key, value in action[3].items():
		#	create_timestamp_tag(correct_timestamps, 'correct_timestamp', key, value)
		
		#wrong_timestamps = SubElement(accuracy, 'wrong_timestamps')
		#for key, value in action[4].items():
		#	create_timestamp_tag(wrong_timestamps, 'wrong_timestamp', key, value)
		

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
			generate_XML(actions, output_filename, data)
	

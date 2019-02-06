import sys
import json
from datetime import datetime

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom

#constants
MEDIA_DB_FILE = "media.db"
AXOLOTL_DB_FILE = "axolotl.db"
C_TIME = "ctime"
M_TIME = "mtime"
SEND_OR_RECEIVE_PHOTO = "send_or_receive_photo"
SEND_OR_RECEIVE_TEXT = "send_or_receive_text"


def total_seconds (time):
	"""Convert input time to seconds since epoch"""
	input_time = datetime.strptime(str(time),'%d-%b-%Y, %H:%M:%S')
	epoch = datetime.strptime("01-Jan-1970, 00:00:00",'%d-%b-%Y, %H:%M:%S')
	return int((input_time - epoch).total_seconds())

def passes_threshold (time_one, time_two):
	return abs(total_seconds(time_one) - total_seconds(time_two)) < threshold

def is_file_available (data, filename):
	"""Return True is the given file is available in the input data file, otherwise return False"""
	return True if filename in data else False

def find_accuracy (data, passes_threshold, total_count):
	"""data is the input data file. passes_threshold - is True if the diff of TS values is less than threshold
	total_count - total count of files that should change its timestamps.""" 
	correct_file_name_and_ts = {}
	wrong_file_name_and_ts = {}
	if total_count == 1:  # send_or_receive_text
		accuracy_perc = 100
		correct_file_name_and_ts[AXOLOTL_DB_FILE] = data[AXOLOTL_DB_FILE][C_TIME]
	elif total_count == 2: # send_or_receive_photo
		if passes_threshold: # ctime diff of media and axolotl db files is less than threshold
			accuracy_perc = 100
			correct_file_name_and_ts[AXOLOTL_DB_FILE] = data[AXOLOTL_DB_FILE][C_TIME]
		else:
			accuracy_perc = 50
			wrong_file_name_and_ts[AXOLOTL_DB_FILE] = data[AXOLOTL_DB_FILE][C_TIME]
		correct_file_name_and_ts[MEDIA_DB_FILE] = data[MEDIA_DB_FILE][C_TIME]

	return (accuracy_perc, correct_file_name_and_ts, wrong_file_name_and_ts)

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
			is_passes_threshold = passes_threshold(data[AXOLOTL_DB_FILE][C_TIME], data[MEDIA_DB_FILE][C_TIME])
			if is_passes_threshold:
				accuracy = find_accuracy(data, is_passes_threshold, 2)
				result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME], accuracy))
			else:
				accuracy = find_accuracy(data, is_passes_threshold, 1)
				result.append((SEND_OR_RECEIVE_TEXT, data[AXOLOTL_DB_FILE][C_TIME], accuracy))
				accuracy = find_accuracy(data, is_passes_threshold, 2)
				result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME], accuracy))
		else:
			accuracy = find_accuracy(data, True, 1)
			result.append((SEND_OR_RECEIVE_TEXT, data[AXOLOTL_DB_FILE][C_TIME], accuracy))

	elif media_changed:
		accuracy = find_accuracy(data, False, 2)
		result.append((SEND_OR_RECEIVE_PHOTO, data[MEDIA_DB_FILE][C_TIME], accuracy))
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
	filename_tag = SubElement (child_tag, 'filename')
	filename_tag.text = key
	timestamp_tag = SubElement(child_tag, 'timestamp')
	timestamp_tag.text = str(value)

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
		action_date.text = str(action[1])
		accuracy_percentage = SubElement(match, 'accuracy_percentage')
		accuracy_percentage.text = str(action[2][0])

		correct_timestamps = SubElement(match, 'correct_timestamps')
		for key, value in action[2][1].items():
			create_timestamp_tag (correct_timestamps, 'correct_timestamp', key, value)

		wrong_timestamps = SubElement(match, 'wrong_timestamps')
		if len(action[2][2]) > 0:
			for key, value in action[2][2].items():
				create_timestamp_tag (wrong_timestamps, 'wrong_timestamp', key, value)
		

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
	
